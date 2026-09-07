from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserSchemaBase(BaseModel):
    # Shared model config keeps response models compatible with ORM objects.
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserSchemaBase):
    # Payload used when a new user account is created.
    full_name: str = Field(min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Optional[UserRole] = Field(default=UserRole.EMPLOYEE)


class UserLogin(BaseModel):
    # Credentials used to authenticate an existing user.
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(UserSchemaBase):
    # Partial update payload for user profile and account status changes.
    full_name: Optional[str] = Field(default=None, min_length=3, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    is_active: Optional[bool] = None


class UserResponse(UserSchemaBase):
    # Public user representation returned by API endpoints.
    id: str
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
