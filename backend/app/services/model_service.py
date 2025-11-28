import enum
import logging
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..domain.ml.models import ModelStatus, ModelVersion

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    import mlflow.pyfunc as mlflow_pyfunc
except Exception:  # noqa: BLE001
    mlflow_pyfunc = None


class ModelTier(str, enum.Enum):
    FREEMIUM = "FREEMIUM"
    PLUS = "PLUS"
    ENTERPRISE = "ENTERPRISE"


async def resolve_model_uri_for_tier(
    db: AsyncSession, tier: ModelTier, enterprise_slug: str | None = None
) -> tuple[str, str]:
    query = select(ModelVersion).where(ModelVersion.tier == tier.value, ModelVersion.status == ModelStatus.CHAMPION)
    if tier == ModelTier.ENTERPRISE and enterprise_slug:
        query = query.where(ModelVersion.enterprise_slug == enterprise_slug)
    result = await db.execute(query.order_by(ModelVersion.created_at.desc()))
    champion = result.scalars().first()

    if champion:
        logger.info("Using champion model for tier %s (source: db)", tier.value)
        return champion.mlflow_model_uri, "champion_db"

    uri = _default_model_uri_for_tier(tier)
    logger.info("Using default model URI for tier %s (source: settings)", tier.value)
    return uri, "default_settings"


@lru_cache(maxsize=32)
def load_model_from_uri(uri: str) -> Any:
    use_mlflow = bool(settings.MLFLOW_TRACKING_URI) and mlflow_pyfunc is not None and _looks_like_mlflow_uri(uri)
    if use_mlflow:
        try:
            model = mlflow_pyfunc.load_model(uri)
            logger.info("Loaded model via MLflow from %s", uri)
            return model
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load model via MLflow from %s; falling back to pickle: %s", uri, exc)

    model = _load_pickle_model(uri)
    logger.info("Loaded model via pickle from %s", uri)
    return model


async def predict_for_tier(
    db: AsyncSession, tier: ModelTier, features: dict, enterprise_slug: str | None = None
) -> Any:
    uri, source = await resolve_model_uri_for_tier(db, tier, enterprise_slug)
    model = load_model_from_uri(uri)

    if not hasattr(model, "predict"):
        raise AttributeError("Loaded model does not implement predict()")

    X = _features_to_input(features)
    raw = model.predict(X)
    normalized = _normalize_output(raw)
    if normalized is raw:
        logger.debug("Prediction output has unexpected shape/type (%s) from source %s", type(raw), source)
    return normalized


def _features_to_input(features: dict) -> np.ndarray:
    if not isinstance(features, dict):
        raise TypeError("features must be a dict")
    keys = sorted(features.keys())
    values = [features[k] for k in keys]
    return np.array([values])


def _normalize_output(raw: Any) -> Any:
    try:
        if raw is None:
            return None
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, (list, tuple)):
            if len(raw) == 1:
                return _to_float(raw[0])
            return [_to_float(item) for item in raw]
        if isinstance(raw, np.ndarray):
            if raw.size == 1:
                return _to_float(raw.item())
            return raw.tolist()
        if isinstance(raw, (np.generic,)):
            return _to_float(raw)
    except Exception:  # noqa: BLE001
        logger.debug("Failed to normalize prediction output", exc_info=True)
    return raw


def _to_float(value: Any) -> float | Any:
    try:
        if isinstance(value, np.generic):
            return float(value.item())
        return float(value)
    except Exception:
        return value


def _looks_like_mlflow_uri(uri: str) -> bool:
    prefixes = ("runs:/", "models:/", "s3://", "http://", "https://")
    return uri.startswith(prefixes)


def _load_pickle_model(uri: str) -> Any:
    path = Path(uri)
    if not path.exists():
        raise FileNotFoundError(f"Model artifact not found at {uri}")
    with path.open("rb") as file:
        return pickle.load(file)


def _default_model_uri_for_tier(tier: ModelTier) -> str:
    if tier == ModelTier.FREEMIUM:
        uri = settings.DEFAULT_MODEL_URI_FREEMIUM
    elif tier == ModelTier.PLUS:
        uri = settings.DEFAULT_MODEL_URI_PLUS
    else:
        uri = settings.DEFAULT_MODEL_URI_ENTERPRISE

    if uri is None:
        raise RuntimeError(f"No default model URI configured for tier {tier.value}")
    return uri
