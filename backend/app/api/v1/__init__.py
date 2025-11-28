from fastapi import APIRouter

from . import auth, plans, signals, trades, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(plans.router)
api_router.include_router(signals.router)
api_router.include_router(trades.router)

__all__ = ["api_router"]
