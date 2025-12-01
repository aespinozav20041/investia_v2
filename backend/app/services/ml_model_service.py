from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import torch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import PlanEnum, User
from ml.model_registry import get_latest_model_uri
from ml.utils import SimpleLSTMClassifier


class MLModelService:
    """Load, cache, and score ML models per plan."""

    async def get_model_uri_for_plan(self, plan: str, db: AsyncSession) -> str | None:
        plan_key = self._normalize_plan(plan)
        uri = await get_latest_model_uri(plan_key, db_session=db)
        return uri

    async def get_active_model_uri(self, plan: str, db: AsyncSession) -> str | None:
        return await self.get_model_uri_for_plan(plan, db)

    def _normalize_plan(self, plan: str) -> str:
        if plan.lower() == PlanEnum.enterprise.value:
            return PlanEnum.enterprise.value
        if plan.lower() in {PlanEnum.pro.value, "plus"}:
            return PlanEnum.pro.value
        return PlanEnum.free.value

    @lru_cache(maxsize=16)
    def load_model(self, uri: str) -> Any:
        path = Path(uri)
        if not path.exists():
            raise FileNotFoundError(f"Model artifact not found at {uri}")

        if path.suffix == ".pt":  # LSTM
            payload = torch.load(path, map_location="cpu")
            model = SimpleLSTMClassifier(payload["input_dim"], payload.get("hidden_dim", 32))
            model.load_state_dict(payload["state_dict"])
            model.eval()
            payload["model"] = model
            return payload

        return joblib.load(path)

    # Alias matching requested naming
    load_model_from_uri = load_model

    async def predict_signal(self, plan: str, feature_dict: dict[str, float], db: AsyncSession) -> int:
        plan_key = self._normalize_plan(plan)
        uri = await self.get_model_uri_for_plan(plan_key, db)
        if not uri:
            score = feature_dict.get("sentiment_score", 0.0) * 0.6 + feature_dict.get("log_return", 0)
            return 1 if score >= 0 else 0

        model_obj = self.load_model(uri)
        feature_order = model_obj.get("feature_order") if isinstance(model_obj, dict) else None

        if isinstance(model_obj, dict) and model_obj.get("model"):
            model = model_obj["model"]
            if model.__class__.__name__ == "SimpleLSTMClassifier":
                seq_len = model_obj.get("seq_len", 10)
                feature_order = model_obj.get("feature_order", list(feature_dict.keys()))
                vector = np.array([feature_dict.get(f, 0.0) for f in feature_order], dtype=np.float32)
                sequence = np.tile(vector, (seq_len, 1)).reshape(1, seq_len, -1)
                with torch.no_grad():
                    logits = model(torch.tensor(sequence, dtype=torch.float32))
                    pred_idx = torch.argmax(logits, dim=1).item()
                    if logits.shape[1] == 3:
                        return [-1, 0, 1][pred_idx]
                    return int(pred_idx)

        model = model_obj["model"] if isinstance(model_obj, dict) and "model" in model_obj else model_obj
        feature_order = feature_order or list(feature_dict.keys())
        vector = np.array([feature_dict.get(f, 0.0) for f in feature_order]).reshape(1, -1)
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(vector)[0][1]
            return 1 if proba >= 0.5 else 0
        pred = model.predict(vector)[0]
        return int(pred)

    async def generate_signal_for_user(self, user: User, feature_dict: dict[str, float], db: AsyncSession) -> int:
        plan_value = user.plan.value if isinstance(user.plan, PlanEnum) else str(user.plan)
        return await self.predict_signal(plan_value, feature_dict, db)

    async def predict_signal_for_plan(self, plan: str, feature_dict: dict[str, float], db: AsyncSession) -> int:
        return await self.predict_signal(plan, feature_dict, db)


ml_model_service = MLModelService()
