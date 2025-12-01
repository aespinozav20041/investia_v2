from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.services.ml_model_service import ml_model_service
from ml.model_registry import list_all_versions, register_model_version, get_latest_model_uri

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/latest")
async def latest_models(db: AsyncSession = Depends(deps.get_db)):
    versions = await list_all_versions(session=db)
    latest = {}
    for version in versions:
        if version.plan not in latest:
            latest[version.plan] = {
                "uri": version.uri,
                "sharpe": version.sharpe,
                "win_rate": version.win_rate,
                "created_at": version.created_at,
            }
    return latest


@router.get("/test")
async def test_model(plan: str = Query("free", pattern="^(free|pro|enterprise)$"), db: AsyncSession = Depends(deps.get_db)):
    uri = await get_latest_model_uri(plan, session=db)
    if not uri:
        raise HTTPException(status_code=404, detail="No model registered for plan")
    dummy_features = {
        "return_1d": 0.01,
        "volatility_5": 0.02,
        "volatility_10": 0.03,
        "volatility_20": 0.04,
        "ma_ratio": 1.01,
        "rsi_14": 55,
        "volume_zscore": 0.2,
        "price_spread": 0.4,
        "sentiment_score": 0.1,
        "orderbook_depth": 0.5,
        "quant_factor": 0.5,
    }
    signal = await ml_model_service.predict_signal(plan, dummy_features, db)
    return {"plan": plan, "uri": uri, "signal": signal}


@router.post("/promote")
async def promote_model(
    payload: dict,
    db: AsyncSession = Depends(deps.get_db),
):
    plan = payload.get("plan")
    uri = payload.get("uri")
    sharpe = float(payload.get("sharpe", 0))
    win_rate = float(payload.get("win_rate", 0))
    if not plan or not uri:
        raise HTTPException(status_code=400, detail="plan and uri are required")
    version = await register_model_version(plan, uri, sharpe, win_rate)
    ml_model_service.load_model.cache_clear()
    return {"id": version.id, "plan": version.plan, "uri": version.uri}
