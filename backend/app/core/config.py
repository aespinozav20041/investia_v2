from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENVIRONMENT: str = Field("development", description="Environment name: development or production")
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_SSL: bool = False

    ALLOWED_ORIGINS: List[str] = [
        "https://investia.live",
        "https://www.investia.live",
        "https://api.investia.live"
    ]

    ENABLE_LIVE_TRADING: bool = False
    ENABLE_PAPER_TRADING: bool = True
    MAX_DAILY_LOSS_PCT: float = 0.05

    ALPACA_API_KEY: Optional[str] = None
    ALPACA_API_SECRET: Optional[str] = None
    ALPACA_BASE_URL: Optional[str] = None

    MLFLOW_TRACKING_URI: Optional[str] = None
    DEFAULT_MODEL_URI_FREEMIUM: Optional[str] = None
    DEFAULT_MODEL_URI_PLUS: Optional[str] = None


@lru_cache

def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
