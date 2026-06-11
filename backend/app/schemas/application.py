"""Pydantic request/response shapes for POST /applications."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.application import ApplicationStatus, ClassLevel


# Nigerian mobile numbers in either international (+234XXXXXXXXXX) or
# local (0XXXXXXXXXX) form. 10 digits after the prefix.
_NIGERIAN_PHONE_RE = re.compile(r"^(\+234|0)\d{10}$")


class ApplicationCreate(BaseModel):
    """Body for POST /applications."""

    child_name: str = Field(..., min_length=1, max_length=200)
    guardian_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., max_length=20)
    class_level: ClassLevel
    message: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-()]+", "", v)
        if not _NIGERIAN_PHONE_RE.match(cleaned):
            raise ValueError(
                "Phone must be a Nigerian number "
                "(+234XXXXXXXXXX or 0XXXXXXXXXX)."
            )
        return cleaned


class ApplicationResponse(BaseModel):
    """What we hand back to the client after a successful POST."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: ApplicationStatus
    created_at: datetime
