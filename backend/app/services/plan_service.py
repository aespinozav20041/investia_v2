import logging
from datetime import date, datetime, time, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..domain.plans.models import Plan
from ..domain.trading.models import Signal, Trade
from ..domain.users.models import User

logger = logging.getLogger(__name__)
settings = get_settings()


class PlanLimitExceeded(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


async def get_user_with_plan(db: AsyncSession, user_id: str) -> tuple[User, Plan]:
    result = await db.execute(select(User, Plan).join(Plan, Plan.id == User.plan_id).where(User.id == user_id))
    row = result.first()
    if not row:
        raise ValueError("User or plan not found")
    user, plan = row
    return user, plan


def _start_of_today_utc() -> datetime:
    now = datetime.now(timezone.utc)
    today = now.date()
    return datetime.combine(today, time.min, tzinfo=timezone.utc)


async def count_user_signals_today(db: AsyncSession, user_id: str) -> int:
    start_of_day = _start_of_today_utc()
    result = await db.execute(
        select(func.count(Signal.id)).where(Signal.user_id == user_id, Signal.timestamp >= start_of_day)
    )
    count = result.scalar_one_or_none() or 0
    logger.debug("User %s signal count today: %s", user_id, count)
    return int(count)


async def get_user_daily_pnl(db: AsyncSession, user_id: str) -> float:
    start_of_day = _start_of_today_utc()
    result = await db.execute(
        select(func.coalesce(func.sum(Trade.pnl), 0)).where(Trade.user_id == user_id, Trade.closed_at >= start_of_day)
    )
    pnl = result.scalar_one_or_none() or 0
    logger.debug("User %s daily PnL: %s", user_id, pnl)
    return float(pnl)


async def enforce_plan_limits_for_signal(
    db: AsyncSession,
    user: User,
    plan: Plan,
    symbol: str,
    notional: float | None = None,
) -> None:
    signal_count = await count_user_signals_today(db, str(user.id))
    if signal_count >= plan.max_signals_per_day:
        message = "daily signal limit reached"
        logger.warning("User %s exceeded signals per day limit (%s)", user.id, plan.max_signals_per_day)
        raise PlanLimitExceeded(message)

    if notional is not None and plan.max_capital_per_user is not None:
        try:
            if float(notional) > float(plan.max_capital_per_user):
                message = "requested notional exceeds plan limit"
                logger.warning(
                    "User %s notional %.2f exceeds plan limit %.2f", user.id, float(notional), float(plan.max_capital_per_user)
                )
                raise PlanLimitExceeded(message)
        except Exception:  # noqa: BLE001
            logger.debug("Could not compare notional to plan limit for user %s", user.id, exc_info=True)

    if plan.allowed_symbols is not None and symbol not in plan.allowed_symbols:
        message = "symbol not allowed in current plan"
        logger.warning("User %s tried symbol %s not allowed for plan %s", user.id, symbol, plan.code)
        raise PlanLimitExceeded(message)


async def check_daily_loss_limit(db: AsyncSession, user: User) -> bool:
    _ = await get_user_daily_pnl(db, str(user.id))
    logger.info(
        "TODO: enforce MAX_DAILY_LOSS_PCT (%s) per user using equity baseline and realized/unrealized PnL",
        settings.MAX_DAILY_LOSS_PCT,
    )
    return True


# Existing plan/listing helpers preserved for API usage.
async def list_plans(db: AsyncSession) -> List[Plan]:
    result = await db.execute(select(Plan))
    return result.scalars().all()


async def get_signals_for_user_today(
    db: AsyncSession, user_id, start_of_day: Optional[datetime] = None
) -> List[Signal]:
    if start_of_day is None:
        start_of_day = _start_of_today_utc()
    result = await db.execute(
        select(Signal).where(Signal.user_id == user_id, Signal.timestamp >= start_of_day).order_by(Signal.timestamp.desc())
    )
    return result.scalars().all()


async def get_trades_for_user(
    db: AsyncSession,
    user_id,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Trade]:
    query = select(Trade).where(Trade.user_id == user_id)
    if start_date:
        query = query.where(Trade.opened_at >= start_date)
    if end_date:
        query = query.where(Trade.opened_at <= end_date)
    result = await db.execute(query.order_by(Trade.opened_at.desc()))
    return result.scalars().all()
