import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1 import auth, users, plans, signals, trades
from .core.config import get_settings
from .core.logging import setup_logging

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Investia API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):  # type: ignore[override]
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def healthcheck():
    return {"status": "ok", "env": settings.ENVIRONMENT}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")
app.include_router(signals.router, prefix="/api/v1")
app.include_router(trades.router, prefix="/api/v1")
