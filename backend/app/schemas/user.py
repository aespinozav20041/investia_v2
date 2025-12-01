from pydantic import BaseModel, EmailStr

from app.models.user import PlanEnum


class UserBase(BaseModel):
    email: EmailStr
    plan: PlanEnum = PlanEnum.free
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True
