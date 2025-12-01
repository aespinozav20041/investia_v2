from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration using environment variables."""

    PROJECT_NAME: str = "Investia API"
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = Field(..., description="Async database URL")
    REDIS_URL: str = Field(..., description="Redis connection URL")

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "https://investia.live",
        "https://www.investia.live",
        "https://api.investia.live",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    ENCRYPTION_SECRET_KEY: str = Field(..., description="Key used to encrypt broker secrets")

    MODEL_PROVIDER: str = "openai"
    MODEL_NAME: str = "gpt-4.1-mini"
    OPENAI_API_KEY: str | None = None

    MERCADOPAGO_ACCESS_TOKEN: str = Field(..., description="Mercado Pago server token")
    MERCADOPAGO_PUBLIC_KEY: str = Field(..., description="Mercado Pago public key")
    MERCADOPAGO_WEBHOOK_TOKEN: str = Field(..., description="Webhook secret token")
    FRONTEND_URL: AnyHttpUrl = "https://investia.live"
    BACKEND_URL: AnyHttpUrl = "https://api.investia.live"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
