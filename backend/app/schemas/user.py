"""Pydantic schemas for user-facing auth endpoints."""

import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole, UserStatus


_NIGERIAN_PHONE_RE = re.compile(r"^(\+234|0)\d{10}$")


class RegisterRequest(BaseModel):
    """Body for ``POST /auth/register`` — parent self-signup."""

    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Minimum 8 characters. Will be hashed server-side with argon2id.",
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        cleaned = re.sub(r"[\s\-()]+", "", v)
        if not _NIGERIAN_PHONE_RE.match(cleaned):
            raise ValueError(
                "Phone must be a Nigerian number "
                "(+234XXXXXXXXXX or 0XXXXXXXXXX)."
            )
        return cleaned


class UserResponse(BaseModel):
    """Public representation of a User — no password hash ever included."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    created_at: datetime


class LoginRequest(BaseModel):
    """Body for ``POST /auth/login``."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class ForgotPasswordRequest(BaseModel):
    """Body for ``POST /auth/forgot-password``."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Body for ``POST /auth/reset-password``."""

    token: str = Field(..., min_length=10, max_length=200)
    new_password: str = Field(..., min_length=8, max_length=128)
