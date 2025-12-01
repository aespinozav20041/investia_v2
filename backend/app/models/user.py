from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as PgEnum, Integer, String, func

from app.core.database import Base


class PlanEnum(str, Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    plan = Column(PgEnum(PlanEnum), default=PlanEnum.free, nullable=False)
    upgraded_at = Column(DateTime(timezone=True), nullable=True)
    enterprise_requested = Column(Boolean, default=False, nullable=False)
    last_payment_id = Column(String, nullable=True)
    last_payment_status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
