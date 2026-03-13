from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    given_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=256)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    given_name: str
    last_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthSession(BaseModel):
    message: str
    user: UserRead
