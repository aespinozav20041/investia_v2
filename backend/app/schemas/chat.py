from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    trade_id: int | None = None


class ChatResponse(BaseModel):
    answer: str
