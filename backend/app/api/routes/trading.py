from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.services.trading_engine import trading_engine
from app.services.ml_model_service import ml_model_service

router = APIRouter(prefix="/trading", tags=["trading"])


@router.get("/signal")
async def get_signal(
    symbol: str = Query("BTC-USD"),
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
):
    features = trading_engine.build_realtime_features(symbol)
    signal = await ml_model_service.generate_signal_for_user(current_user, features, db)
    side = "buy" if signal == 1 else ("sell" if signal == -1 else "flat")
    return {
        "plan_used": getattr(current_user.plan, "value", current_user.plan),
        "symbol": symbol,
        "side": side,
        "price": round(features.get("price", 0.0), 4),
        "timestamp": datetime.utcnow().isoformat(),
        "features": features,
    }
