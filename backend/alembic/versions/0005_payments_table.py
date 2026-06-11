"""payments table

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-11

Creates the payments table that backs Paystack initialize + verify.
See app/models/payment.py.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("payer_id", sa.Uuid(), nullable=False),
        sa.Column("reference", sa.String(length=64), nullable=False),
        sa.Column("amount_kobo", sa.Integer(), nullable=False),
        sa.Column(
            "purpose",
            sa.Enum("fees", "programme", name="payment_purpose"),
            nullable=False,
        ),
        sa.Column("target", sa.String(length=80), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "success", "failed", name="payment_status"
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "verified_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["payer_id"], ["users.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_payer_id", "payments", ["payer_id"])
    op.create_index(
        "ix_payments_reference", "payments", ["reference"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_payments_reference", table_name="payments")
    op.drop_index("ix_payments_payer_id", table_name="payments")
    op.drop_table("payments")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="payment_purpose").drop(bind, checkfirst=False)
        sa.Enum(name="payment_status").drop(bind, checkfirst=False)
