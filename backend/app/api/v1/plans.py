from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db import get_db
from ...services.plan_service import list_plans

router = APIRouter(prefix="/plans", tags=["plans"])


class PlanPublic(BaseModel):
    code: str
    name: str
    max_signals_per_day: int
    max_capital_per_user: float
    data_delay_seconds: int


@router.get("/", response_model=list[PlanPublic])
async def get_plans(db: AsyncSession = Depends(get_db)):
    plans = await list_plans(db)
    return [
        PlanPublic(
            code=plan.code,
            name=plan.name,
            max_signals_per_day=plan.max_signals_per_day,
            max_capital_per_user=float(plan.max_capital_per_user),
            data_delay_seconds=plan.data_delay_seconds,
        )
        for plan in plans
    ]
