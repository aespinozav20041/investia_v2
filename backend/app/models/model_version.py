from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.core.database import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    plan = Column(String, nullable=False, index=True)
    uri = Column(String, nullable=False)
    sharpe = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
