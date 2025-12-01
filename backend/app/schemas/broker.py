from pydantic import BaseModel


class BrokerConnect(BaseModel):
    broker_name: str
    api_key: str
    api_secret: str
    live_trading_enabled: bool = False


class BrokerConnectionRead(BaseModel):
    id: int
    broker_name: str
    is_live_trading_enabled: bool

    class Config:
        orm_mode = True
