import asyncio
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trading import Trade
from app.models.user import User
from app.services.portfolio_service import portfolio_service
from app.services.trading_engine import trading_engine


async def generate_paper_trades_for_users(db: AsyncSession) -> None:
    """Simulate paper trades for each active user."""
    users = (await db.execute(select(User).where(User.is_active == True))).scalars().all()  # noqa: E712
    for user in users:
        event = await trading_engine.generate_trade_event(db, user=user)
        await trading_engine.record_trade(db, event["trade"])
        await asyncio.sleep(0)  # yield control


async def recompute_daily_metrics(db: AsyncSession) -> None:
    """Aggregate trades into DailyMetrics (simplified)."""
    users = (await db.execute(select(User).where(User.is_active == True))).scalars().all()  # noqa: E712
    for user in users:
        result = await db.execute(
            select(func.coalesce(func.sum(Trade.pnl), 0), func.count(Trade.id)).where(Trade.user_id == user.id)
        )
        pnl, trade_count = result.one()
        win_rate = 0.0
        if trade_count:
            wins = await db.execute(
                select(func.count(Trade.id)).where(Trade.user_id == user.id, Trade.pnl > 0)
            )
            win_rate = wins.scalar_one() / trade_count
        sharpe_ratio = 1.2 if trade_count else 0.0  # placeholder
        await portfolio_service.upsert_daily_metric(
            db,
            user_id=user.id,
            metric_date=date.today(),
            pnl=float(pnl or 0),
            sharpe_ratio=float(sharpe_ratio),
            win_rate=float(win_rate),
        )
