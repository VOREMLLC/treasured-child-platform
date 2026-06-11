"""Pydantic request/response shapes for /payments."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentPurpose, PaymentStatus


class PaymentInitializeRequest(BaseModel):
    """Body for ``POST /payments/initialize``."""

    purpose: PaymentPurpose
    target: Optional[str] = Field(
        default=None,
        max_length=80,
        description=(
            "Programme slug when ``purpose=programme`` "
            "(e.g. 'bece-prep'). Ignored when ``purpose=fees``."
        ),
    )


class PaymentInitializeResponse(BaseModel):
    """Returned to the frontend to set up the Paystack inline widget."""

    reference: str
    amount_kobo: int
    public_key: str
    payer_email: str
    purpose: PaymentPurpose
    target: Optional[str]


class PaymentVerifyRequest(BaseModel):
    """Body for ``POST /payments/verify``."""

    reference: str = Field(..., min_length=1, max_length=64)


class PaymentResponse(BaseModel):
    """Public read shape for a Payment row — no raw_response leaked."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference: str
    amount_kobo: int
    purpose: PaymentPurpose
    target: Optional[str]
    status: PaymentStatus
    verified_at: Optional[datetime]
    created_at: datetime
