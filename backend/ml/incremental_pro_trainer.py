"""Scheduled incremental trainer for PRO plan."""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

import joblib
import xgboost as xgb

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.core.database import AsyncSessionLocal  # noqa: E402
from ml import utils  # noqa: E402
from ml.model_registry import get_latest_model_uri, register_model_version  # noqa: E402
from ml.train_pro_model import SYMBOL, INTERVAL, train_pro_model  # noqa: E402


def load_existing_model(uri: str) -> Tuple[xgb.XGBClassifier, list[str]]:
    payload = joblib.load(uri)
    if isinstance(payload, dict) and "model" in payload:
        return payload["model"], payload.get("feature_order", [])
    return payload, payload["feature_order"] if isinstance(payload, dict) and "feature_order" in payload else []


async def incremental_update(register: bool = True) -> Tuple[Path, dict]:
    async with AsyncSessionLocal() as session:
        current_uri = await get_latest_model_uri("pro", db_session=session)
        if not current_uri:
            # Bootstrap
            path, metrics = train_pro_model(register=register)
            return path, metrics

        model, feature_order = load_existing_model(current_uri)
        df = utils.load_ohlcv(SYMBOL, INTERVAL)
        features, target = utils.build_features_pro(df)
        window_df = utils.recent_window(features.join(target.rename("target")), days=120)
        features_win = window_df[feature_order] if feature_order else window_df.drop(columns=["target"])
        target_win = window_df["target"]

        # Train new model on rolling window
        candidate = xgb.XGBClassifier(
            n_estimators=180,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            eval_metric="logloss",
            random_state=42,
        )
        candidate.fit(features_win, target_win)

        # Evaluate old vs new on last 25%
        split_idx = int(len(features_win) * 0.75)
        X_val, y_val = features_win.iloc[split_idx:], target_win.iloc[split_idx:]
        old_preds = model.predict(X_val)
        new_preds = candidate.predict(X_val)
        returns = X_val["log_return"]
        old_metrics = utils.compute_strategy_metrics(returns, old_preds)
        new_metrics = utils.compute_strategy_metrics(returns, new_preds)

        if new_metrics["sharpe"] <= old_metrics["sharpe"]:
            return Path(current_uri), old_metrics

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        model_path = utils.MODEL_DIR / f"pro_signal_model_incremental_{SYMBOL}_{INTERVAL}_{timestamp}.pkl"
        utils.save_model(candidate, model_path, feature_order or list(features_win.columns), extra={"metrics": new_metrics})
        if register:
            await register_model_version("pro", str(model_path), new_metrics["sharpe"], new_metrics["win_rate"], session)
        return model_path, new_metrics


if __name__ == "__main__":
    path, metrics = asyncio.run(incremental_update(register=True))
    print("Incremental PRO model saved to", path)
    print("Metrics", metrics)
