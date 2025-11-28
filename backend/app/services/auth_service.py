from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import hash_password, verify_password
from ..domain.plans.models import Plan
from ..domain.users.models import User


async def create_user(db: AsyncSession, email: str, password: str, plan_code: str) -> User:
    plan_result = await db.execute(select(Plan).where(Plan.code == plan_code))
    plan = plan_result.scalar_one_or_none()
    if plan is None:
        raise ValueError("Invalid plan code")

    existing_user = await db.execute(select(User).where(User.email == email))
    if existing_user.scalar_one_or_none():
        raise ValueError("User already exists")

    user = User(email=email, password_hash=hash_password(password), plan_id=plan.id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password_hash):
        return user
    return None
