from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.models import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Optional[UserRole] = UserRole.reader

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True #SQLALCHEMY відправляє обєкти, а Pydantic по дефолту очікує словник
