"""applications table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-11

Creates the applications table that backs POST /applications and the
admin applications queue. See app/models/application.py.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("child_name", sa.String(length=200), nullable=False),
        sa.Column("guardian_name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column(
            "class_level",
            sa.Enum(
                "nursery",
                "primary",
                "junior_secondary",
                "senior_secondary",
                name="class_level",
            ),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "new",
                "contacted",
                "enrolled",
                "rejected",
                name="application_status",
            ),
            nullable=False,
            server_default="new",
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_applications_email", "applications", ["email"]
    )


def downgrade() -> None:
    op.drop_index("ix_applications_email", table_name="applications")
    op.drop_table("applications")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="class_level").drop(bind, checkfirst=False)
        sa.Enum(name="application_status").drop(bind, checkfirst=False)
