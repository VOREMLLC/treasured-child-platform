"""Payment model — one row per payment attempt.

A Payment is created in ``pending`` state by ``POST /payments/initialize``.
After the user completes the Paystack inline flow and the frontend
calls ``POST /payments/verify``, the server hits Paystack's verify API
with the secret key, compares the confirmed amount to the
server-computed expected amount, and transitions the row to ``success``
(or ``failed`` on amount mismatch).

The verify path is idempotent: re-verifying an already-success row
returns the cached state without re-contacting Paystack.

Money is always stored as integer **kobo** (Naira × 100).
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PaymentPurpose(str, enum.Enum):
    """What this payment is for."""

    fees = "fees"
    programme = "programme"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    payer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    # Server-generated; unique; the value passed to Paystack as `ref`.
    reference: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    amount_kobo: Mapped[int] = mapped_column(Integer, nullable=False)
    purpose: Mapped[PaymentPurpose] = mapped_column(
        Enum(PaymentPurpose, name="payment_purpose"),
        nullable=False,
    )
    # Programme slug when purpose=programme; NULL otherwise.
    target: Mapped[Optional[str]] = mapped_column(
        String(80), nullable=True
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        nullable=False,
        default=PaymentStatus.pending,
        server_default=PaymentStatus.pending.value,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Full Paystack verify response, stored for audit.
    raw_response: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Payment id={self.id} reference={self.reference!r} "
            f"status={self.status.value} amount_kobo={self.amount_kobo}>"
        )
