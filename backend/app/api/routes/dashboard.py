from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.trading import Trade
from app.models.user import PlanEnum, User
from app.schemas.trading import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    *, db: AsyncSession = Depends(deps.get_db), current_user: User = Depends(deps.get_current_active_user)
):
    result = await db.execute(
        select(func.coalesce(func.sum(Trade.pnl), 0), func.count(Trade.id)).where(Trade.user_id == current_user.id)
    )
    total_pnl, trades_count = result.one()
    paper_mode = current_user.plan == PlanEnum.free
    return DashboardSummary(total_pnl=float(total_pnl or 0), trades=trades_count, paper_mode=paper_mode)
