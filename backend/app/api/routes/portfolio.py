from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.portfolio import DailyMetricsRead
from app.services.portfolio_service import portfolio_service

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/metrics", response_model=list[DailyMetricsRead])
async def get_metrics(
    *, db: AsyncSession = Depends(deps.get_db), current_user=Depends(deps.get_current_active_user)
):
    metrics = await portfolio_service.get_metrics(db, current_user.id)
    return metrics
