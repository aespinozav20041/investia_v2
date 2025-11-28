from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import get_db
from ...domain.trading.models import Trade
from ...domain.users.models import User
from ...services.plan_service import get_trades_for_user
from .auth import get_current_user

router = APIRouter(prefix="/trades", tags=["trades"])


class TradeResponse(BaseModel):
    id: str
    symbol: str
    side: str
    qty: float
    entry_price: float
    exit_price: float | None
    pnl: float | None
    opened_at: datetime
    closed_at: datetime | None


@router.get("/", response_model=list[TradeResponse])
async def list_trades(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    trades = await get_trades_for_user(db, current_user.id, start_date, end_date)
    return [
        TradeResponse(
            id=str(trade.id),
            symbol=trade.symbol,
            side=trade.side,
            qty=float(trade.qty),
            entry_price=float(trade.entry_price),
            exit_price=float(trade.exit_price) if trade.exit_price is not None else None,
            pnl=float(trade.pnl) if trade.pnl is not None else None,
            opened_at=trade.opened_at,
            closed_at=trade.closed_at,
        )
        for trade in trades
    ]
