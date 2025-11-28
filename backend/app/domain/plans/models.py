import uuid

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...core.db import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    max_signals_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    max_capital_per_user: Mapped[float] = mapped_column(Numeric, nullable=False)
    data_delay_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    is_enterprise: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_symbols: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
