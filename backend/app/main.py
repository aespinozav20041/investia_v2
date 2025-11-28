import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1 import api_router
from .core.config import get_settings
from .core.logging import setup_logging

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Investia API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://investia.live",
        "https://www.investia.live",
        "https://api.investia.live",
        "https://investia-v2-frontend-fq3l-dig0jw9sq-adrians-projects-0775393a.vercel.app",
        "http://localhost:3000"
    ],
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

app.include_router(api_router, prefix="/api/v1")
