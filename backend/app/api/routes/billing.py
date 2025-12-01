from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import settings
from app.models.user import PlanEnum, User

PLAN_PRICES = {"pro": 29.0, "enterprise": 99.0}

router = APIRouter(prefix="/billing", tags=["billing"])


def _validate_plan(plan: str) -> str:
    plan = plan.lower()
    if plan not in ("pro", "enterprise"):
        raise HTTPException(status_code=400, detail="Invalid plan")
    return plan


@router.post("/create-checkout")
async def create_checkout(payload: dict, db: AsyncSession = Depends(deps.get_db), current_user: User = Depends(deps.get_current_active_user)):
    plan = _validate_plan(payload.get("plan", ""))
    if current_user.plan.value == plan:
        raise HTTPException(status_code=400, detail="Already on this plan")

    price = PLAN_PRICES[plan]
    headers = {"Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}"}
    preference_payload = {
        "items": [
            {
                "title": f"INVESTIA {plan.capitalize()} Plan",
                "quantity": 1,
                "currency_id": "USD",
                "unit_price": price,
            }
        ],
        "payer": {"email": current_user.email},
        "back_urls": {
            "success": f"{settings.FRONTEND_URL}/settings/billing?status=success",
            "failure": f"{settings.FRONTEND_URL}/settings/billing?status=failure",
            "pending": f"{settings.FRONTEND_URL}/settings/billing?status=pending",
        },
        "auto_return": "approved",
        "notification_url": f"{settings.BACKEND_URL}/api/v1/billing/webhook/mercadopago?token={settings.MERCADOPAGO_WEBHOOK_TOKEN}",
        "metadata": {"user_id": current_user.id, "plan": plan},
        "external_reference": str(current_user.id),
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post("https://api.mercadopago.com/checkout/preferences", json=preference_payload, headers=headers)
        if resp.status_code >= 300:
            raise HTTPException(status_code=502, detail="Failed to create Mercado Pago preference")
        data = resp.json()

    return {"init_point": data.get("init_point"), "plan": plan}


@router.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request, token: str = Query(None), db: AsyncSession = Depends(deps.get_db)):
    if token != settings.MERCADOPAGO_WEBHOOK_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook token")
    payload = await request.json()
    try:
        payment_id = payload.get("data", {}).get("id") or payload.get("id")
    except Exception:
        payment_id = None
    if not payment_id:
        return {"received": True}

    headers = {"Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}"}
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"https://api.mercadopago.com/v1/payments/{payment_id}", headers=headers)
        if resp.status_code >= 300:
            return {"received": True}
        payment_data = resp.json()

    status_payment = payment_data.get("status")
    metadata = payment_data.get("metadata") or {}
    user_id = metadata.get("user_id") or payment_data.get("external_reference")
    plan = metadata.get("plan")

    if status_payment == "approved" and user_id and plan:
        try:
            user_id_int = int(user_id)
        except Exception:
            user_id_int = None
        if user_id_int is not None:
            result = await db.execute(select(User).where(User.id == user_id_int))
            user = result.scalars().first()
            if user:
                user.plan = PlanEnum(plan)
                user.upgraded_at = datetime.utcnow()
                user.last_payment_id = str(payment_id)
                user.last_payment_status = status_payment
                if plan == PlanEnum.enterprise.value:
                    user.enterprise_requested = True
                await db.commit()
    return {"received": True}


@router.get("/status")
async def billing_status(current_user: User = Depends(deps.get_current_active_user)):
    return {
        "plan": current_user.plan.value if isinstance(current_user.plan, PlanEnum) else current_user.plan,
        "upgraded_at": current_user.upgraded_at,
        "enterprise_requested": current_user.enterprise_requested,
        "last_payment_id": current_user.last_payment_id,
        "last_payment_status": current_user.last_payment_status,
    }


@router.post("/request-enterprise")
async def request_enterprise(current_user: User = Depends(deps.get_current_active_user), db: AsyncSession = Depends(deps.get_db)):
    current_user.enterprise_requested = True
    await db.commit()
    return {"success": True, "enterprise_requested": True}
