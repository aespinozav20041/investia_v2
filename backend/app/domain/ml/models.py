import enum
import uuid

from sqlalchemy import Enum, Numeric, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from ...core.db import Base


class ModelStatus(str, enum.Enum):
    CHAMPION = "CHAMPION"
    CHALLENGER = "CHALLENGER"
    ARCHIVED = "ARCHIVED"


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    tier: Mapped[str] = mapped_column(Text, nullable=False)
    enterprise_slug: Mapped[str | None] = mapped_column(Text, nullable=True)
    symbol_universe: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    status: Mapped[ModelStatus] = mapped_column(Enum(ModelStatus), nullable=False)
    mlflow_run_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    mlflow_model_uri: Mapped[str] = mapped_column(Text, nullable=False)
    sharpe: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    max_drawdown: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    trained_until: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
