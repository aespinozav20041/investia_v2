from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.model_version import ModelVersion


async def register_model_version(plan: str, uri: str, sharpe: float, win_rate: float, db_session: AsyncSession) -> ModelVersion:
    version = ModelVersion(plan=plan, uri=uri, sharpe=sharpe, win_rate=win_rate)
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    return version


async def get_latest_model_uri(plan: str, db_session: AsyncSession) -> Optional[str]:
    result = await db_session.execute(
        select(ModelVersion).where(ModelVersion.plan == plan).order_by(ModelVersion.created_at.desc())
    )
    version = result.scalars().first()
    return version.uri if version else None


async def list_model_versions(plan: str | None, db_session: AsyncSession) -> List[ModelVersion]:
    stmt = select(ModelVersion).order_by(ModelVersion.created_at.desc())
    if plan:
        stmt = stmt.where(ModelVersion.plan == plan)
    result = await db_session.execute(stmt)
    return result.scalars().all()
