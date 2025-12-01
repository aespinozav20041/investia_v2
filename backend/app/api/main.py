import asyncio
import random
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError
from sqlalchemy import select

from app import models as orm_models  # noqa: F401  ensures models are imported for metadata
from app.api.routes import auth, brokers, chat, dashboard, models as model_routes, plans, portfolio, trading
from app.core.config import settings
from app.core.database import AsyncSessionLocal, init_models
from app.core.security import decode_token
from app.models.user import User
from app.services.trading_engine import trading_engine

app = FastAPI(title=settings.PROJECT_NAME)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(portfolio.router)
api_router.include_router(brokers.router)
api_router.include_router(chat.router)
api_router.include_router(plans.router)
api_router.include_router(model_routes.router)
api_router.include_router(trading.router)
app.include_router(api_router)


@app.on_event("startup")
async def on_startup() -> None:
    # Create tables for dev environments; production should rely on Alembic migrations
    await init_models()


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.websocket("/ws/paper-stream")
async def paper_stream(websocket: WebSocket):
    await websocket.accept()
    async with AsyncSessionLocal() as db:
        user = None
        token = websocket.query_params.get("token")
        if token:
            try:
                payload = decode_token(token)
                email = payload.get("sub")
                if email:
                    result = await db.execute(select(User).where(User.email == email))
                    user = result.scalars().first()
            except JWTError:
                user = None
        try:
            while True:
                event = await trading_engine.generate_trade_event(db, user=user, symbol=random.choice(trading_engine.symbols))
                trade = event["trade"]
                if user:
                    await trading_engine.record_trade(db, trade)
                await websocket.send_json({"type": "trade", "payload": trade, "signal": event["signal"]})
                await asyncio.sleep(3)
        except WebSocketDisconnect:
            return


@app.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        return
