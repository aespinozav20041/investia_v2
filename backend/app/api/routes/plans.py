from fastapi import APIRouter

from app.models.plan import AVAILABLE_PLANS
from app.schemas.plan import PlanRead

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/", response_model=list[PlanRead])
async def list_plans():
    return [PlanRead(name=plan.name.value, features=plan.features) for plan in AVAILABLE_PLANS]
