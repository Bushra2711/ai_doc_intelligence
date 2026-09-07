from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema used when creating a new user account."""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="User's full name",
    )

    email: EmailStr = Field(
        ...,
        description="Valid email address",
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plain-text password received only during registration",
    )


class LoginRequest(BaseModel):
    """Request schema used for user authentication."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(
        ...,
        description="Registered user email",
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="User password",
    )


class UserResponse(BaseModel):
    """Safe user representation returned by the API.

    The password or password hash is intentionally never exposed.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: EmailStr
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    """JWT authentication response."""

    access_token: str
    token_type: str = "bearer"