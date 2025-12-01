from datetime import date

from pydantic import BaseModel


class DailyMetricsRead(BaseModel):
    date: date
    pnl: float
    sharpe_ratio: float
    win_rate: float

    class Config:
        orm_mode = True
