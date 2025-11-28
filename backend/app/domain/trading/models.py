import uuid

from sqlalchemy import ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from ...core.db import Base


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    signal_value: Mapped[float] = mapped_column(Numeric, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", backref="signals")


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(Text, nullable=False)
    side: Mapped[str] = mapped_column(Text, nullable=False)
    qty: Mapped[float] = mapped_column(Numeric, nullable=False)
    entry_price: Mapped[float] = mapped_column(Numeric, nullable=False)
    exit_price: Mapped[float] = mapped_column(Numeric, nullable=True)
    pnl: Mapped[float] = mapped_column(Numeric, nullable=True)
    opened_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="trades")
