from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.broker import BrokerConnect, BrokerConnectionRead
from app.services.broker_service import broker_service

router = APIRouter(prefix="/brokers", tags=["brokers"])


@router.post("/connect", response_model=BrokerConnectionRead)
async def connect_broker(
    payload: BrokerConnect,
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(deps.get_current_active_user),
):
    connection = await broker_service.save_connection(
        db,
        user_id=current_user.id,
        broker_name=payload.broker_name,
        api_key=payload.api_key,
        api_secret=payload.api_secret,
        live_trading_enabled=payload.live_trading_enabled,
    )
    return BrokerConnectionRead(
        id=connection.id,
        broker_name=connection.broker_name,
        is_live_trading_enabled=connection.is_live_trading_enabled,
    )
