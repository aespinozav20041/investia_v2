from pydantic import BaseModel


class PlanRead(BaseModel):
    name: str
    features: list[str]
