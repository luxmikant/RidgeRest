from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RoleEnum(str, Enum):
    employee = "employee"
    employer = "employer"


class AuthProviderEnum(str, Enum):
    local = "local"
    google = "google"


class UserSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: RoleEnum
    department: str = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    department: str
    auth_provider: str
    created_at: datetime


class TokenResponse(BaseModel):
    message: str
    user: UserResponse
