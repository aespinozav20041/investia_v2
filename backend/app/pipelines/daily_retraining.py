"""
Daily model retraining flow using Prefect and MLflow.

Example deployment (run manually, not from this module):
prefect deployment build backend/app/pipelines/daily_retraining.py:daily_model_retraining_flow `
  -n daily-freemium-retrain `
  --cron "0 2 * * *"
prefect deployment apply daily_model_retraining_flow-deployment.yaml

A Prefect agent (e.g., running in Railway) must be connected to the same Prefect API.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Tuple

import mlflow
import numpy as np
import pandas as pd
from prefect import flow, get_run_logger, task
from sklearn.ensemble import GradientBoostingClassifier
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.db import AsyncSessionLocal
from ..domain.ml.models import ModelStatus, ModelVersion
from ..services.model_service import ModelTier

logger = logging.getLogger(__name__)
settings = get_settings()


@task
async def load_training_data(db: AsyncSession, tier: ModelTier) -> Tuple[pd.DataFrame, pd.Series]:
    run_logger = get_run_logger()
    # TODO: Replace synthetic dataset with real feature/label query from Postgres.
    run_logger.info("Loading training data for tier %s (synthetic placeholder)", tier.value)

    rng = np.random.default_rng(seed=42)
    n_samples = 500
    n_features = 6
    X_arr = rng.normal(0, 1, size=(n_samples, n_features))
    weights = rng.normal(0, 0.5, size=n_features)
    logits = X_arr @ weights
    y_arr = (logits > 0).astype(int)

    feature_cols = [f"f{i}" for i in range(n_features)]
    X = pd.DataFrame(X_arr, columns=feature_cols)
    y = pd.Series(y_arr, name="label")
    return X, y


@task
def train_candidate_model(X: pd.DataFrame, y: pd.Series, tier: ModelTier) -> Tuple[object, dict]:
    run_logger = get_run_logger()
    run_logger.info("Training candidate model for tier %s", tier.value)

    if len(X) < 10:
        raise ValueError("Insufficient data to train model")

    split_idx = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_train, y_train)

    val_preds = model.predict(X_val)
    accuracy = float((val_preds == y_val).mean())

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_val)[:, 1]
    else:
        probs = model.decision_function(X_val)
        probs = (probs - probs.min()) / (probs.max() - probs.min() + 1e-8)

    returns = (y_val * 2 - 1) * (probs * 2 - 1)  # simple directional proxy
    sharpe_proxy = float(np.mean(returns) / (np.std(returns) + 1e-8))

    metrics = {"accuracy": accuracy, "sharpe_proxy": sharpe_proxy}
    run_logger.info("Validation metrics: %s", metrics)
    return model, metrics


@task
def log_model_to_mlflow(model, metrics: dict, tier: ModelTier) -> Tuple[str, str]:
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_name = f"retrain_{tier.value}_{timestamp}"

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_param("model_type", model.__class__.__name__)
        mlflow.log_param("tier", tier.value)
        if hasattr(model, "get_params"):
            params = model.get_params()
            # Log a subset of hyperparameters to avoid huge payloads
            for key in ("learning_rate", "n_estimators", "max_depth", "subsample"):
                if key in params:
                    mlflow.log_param(key, params[key])

        for k, v in metrics.items():
            mlflow.log_metric(k, v)

        mlflow.sklearn.log_model(model, artifact_path="model")
        run_id = run.info.run_id
        mlflow_model_uri = f"runs:/{run_id}/model"
        logger.info("Logged model to MLflow: run_id=%s uri=%s", run_id, mlflow_model_uri)
        return run_id, mlflow_model_uri


@task
async def get_current_champion(db: AsyncSession, tier: ModelTier) -> ModelVersion | None:
    result = await db.execute(
        select(ModelVersion)
        .where(ModelVersion.tier == tier.value, ModelVersion.status == ModelStatus.CHAMPION)
        .order_by(ModelVersion.created_at.desc())
    )
    return result.scalars().first()


@task
async def register_new_model_version(
    db: AsyncSession,
    tier: ModelTier,
    mlflow_run_id: str,
    mlflow_model_uri: str,
    metrics: dict,
) -> ModelVersion:
    now = datetime.now(timezone.utc)
    candidate = ModelVersion(
        tier=tier.value,
        status=ModelStatus.CHALLENGER,
        mlflow_run_id=mlflow_run_id,
        mlflow_model_uri=mlflow_model_uri,
        sharpe=metrics.get("sharpe_proxy"),
        max_drawdown=metrics.get("max_drawdown"),
        trained_until=now,
    )
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    logger.info("Registered new model version %s for tier %s", candidate.id, tier.value)
    return candidate


@task
async def evaluate_and_promote(db: AsyncSession, tier: ModelTier, candidate: ModelVersion) -> None:
    champion = await get_current_champion.fn(db, tier)  # call underlying function to avoid extra task graph nesting

    def _metric(val):
        return -1e9 if val is None else float(val)

    if champion is None:
        candidate.status = ModelStatus.CHAMPION
        db.add(candidate)
        await db.commit()
        logger.info("Promoted candidate %s to CHAMPION for tier %s (no previous champion)", candidate.id, tier.value)
        return

    if _metric(candidate.sharpe) > _metric(champion.sharpe):
        champion.status = ModelStatus.CHALLENGER
        candidate.status = ModelStatus.CHAMPION
        db.add_all([champion, candidate])
        await db.commit()
        logger.info(
            "Promoted candidate %s to CHAMPION for tier %s, demoted previous champion %s",
            candidate.id,
            tier.value,
            champion.id,
        )
    else:
        logger.info(
            "Candidate %s not promoted for tier %s (sharpe %.4f <= current champion %.4f)",
            candidate.id,
            tier.value,
            _metric(candidate.sharpe),
            _metric(champion.sharpe),
        )


@flow(name="daily_model_retraining")
async def daily_model_retraining_flow(tier: str = "FREEMIUM") -> None:
    run_logger = get_run_logger()
    try:
        model_tier = ModelTier(tier.upper())
    except Exception:
        raise ValueError(f"Invalid tier '{tier}'. Expected one of {[t.value for t in ModelTier]}")

    run_logger.info("Starting daily retraining flow for tier %s", model_tier.value)

    async with AsyncSessionLocal() as session:
        X, y = await load_training_data(session, model_tier)
        model, metrics = train_candidate_model(X, y, model_tier)
        run_id, model_uri = log_model_to_mlflow(model, metrics, model_tier)
        candidate = await register_new_model_version(session, model_tier, run_id, model_uri, metrics)
        await evaluate_and_promote(session, model_tier, candidate)

    run_logger.info("Completed daily retraining flow for tier %s", model_tier.value)


if __name__ == "__main__":
    asyncio.run(daily_model_retraining_flow())
