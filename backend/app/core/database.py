from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Shared declarative base for all ORM models
Base = declarative_base()

# Async engine/session factory
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine,
)


async def get_db() -> AsyncSession:
    """Provide a database session per request."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_models() -> None:
    """Create database tables in absence of migrations (dev convenience)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
