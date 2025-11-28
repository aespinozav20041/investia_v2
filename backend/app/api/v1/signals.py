from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import get_db
from ...domain.trading.models import Signal
from ...domain.users.models import User
from ...services.plan_service import get_signals_for_user_today
from .auth import get_current_user

router = APIRouter(prefix="/signals", tags=["signals"])


class SignalResponse(BaseModel):
    id: str
    symbol: str
    timestamp: datetime
    signal_value: float
    action: str
    model_name: str


@router.get("/today", response_model=list[SignalResponse])
async def read_signals_today(
    current_user: Annotated[User, Depends(get_current_user)], db: AsyncSession = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    start_of_day = datetime(year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc)
    signals = await get_signals_for_user_today(db, current_user.id, start_of_day)
    return [
        SignalResponse(
            id=str(signal.id),
            symbol=signal.symbol,
            timestamp=signal.timestamp,
            signal_value=float(signal.signal_value),
            action=signal.action,
            model_name=signal.model_name,
        )
        for signal in signals
    ]
