"""Schemas for check"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserScema(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=25)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        """Tells pydantic to convert even non-dict objects to json."""
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User was successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LogoutResponse(BaseModel):
    result: str
