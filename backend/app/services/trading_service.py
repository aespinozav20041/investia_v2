from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .plan_service import get_signals_for_user_today, get_trades_for_user
from ..domain.plans.models import Plan
from ..domain.trading.models import Signal
from ..domain.users.models import User


class TradingService:
    """Facade for trading-related operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_signals_today(self, user_id, start_of_day: Optional[datetime] = None):
        return await get_signals_for_user_today(self.db, user_id, start_of_day)

    async def list_trades(self, user_id, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        return await get_trades_for_user(self.db, user_id, start_date, end_date)


async def generate_signal_for_price(
    db: AsyncSession,
    *,
    user: User,
    plan: Plan | None,
    symbol: str,
    price: float,
    previous_price: float | None,
    model_name: str = "naive_rule",
) -> Signal:
    """
    Placeholder signal generation logic.

    Current rule: if price increased since the last tick -> BUY, decreased -> SELL, else HOLD.
    """

    if previous_price is None:
        action = "HOLD"
        signal_value = 0.0
    else:
        delta = price - previous_price
        action = "BUY" if delta > 0 else "SELL" if delta < 0 else "HOLD"
        signal_value = delta

    signal = Signal(
        user_id=user.id,
        symbol=symbol,
        timestamp=datetime.now(timezone.utc),
        signal_value=signal_value,
        action=action,
        model_name=model_name if plan is None else f"{model_name}:{plan.code}",
    )
    db.add(signal)
    await db.commit()
    await db.refresh(signal)
    return signal
