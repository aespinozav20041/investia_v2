from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import DailyMetrics


class PortfolioService:
    async def get_metrics(self, db: AsyncSession, user_id: int) -> list[DailyMetrics]:
        result = await db.execute(
            select(DailyMetrics).where(DailyMetrics.user_id == user_id).order_by(DailyMetrics.date.desc())
        )
        return result.scalars().all()

    async def upsert_daily_metric(
        self, db: AsyncSession, *, user_id: int, metric_date: date, pnl: float, sharpe_ratio: float, win_rate: float
    ) -> DailyMetrics:
        result = await db.execute(
            select(DailyMetrics).where(DailyMetrics.user_id == user_id, DailyMetrics.date == metric_date)
        )
        instance = result.scalars().first()
        if instance:
            instance.pnl = pnl
            instance.sharpe_ratio = sharpe_ratio
            instance.win_rate = win_rate
        else:
            instance = DailyMetrics(
                user_id=user_id, date=metric_date, pnl=pnl, sharpe_ratio=sharpe_ratio, win_rate=win_rate
            )
            db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance


portfolio_service = PortfolioService()
