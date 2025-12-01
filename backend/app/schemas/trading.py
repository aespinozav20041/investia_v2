from datetime import datetime
from pydantic import BaseModel


class TradeRead(BaseModel):
    id: int
    symbol: str
    side: str
    quantity: float
    price: float
    pnl: float
    explanation: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True


class DashboardSummary(BaseModel):
    total_pnl: float
    trades: int
    paper_mode: bool = True
