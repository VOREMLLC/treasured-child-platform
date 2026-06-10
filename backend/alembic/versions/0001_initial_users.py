"""initial users table

Revision ID: 0001
Revises:
Create Date: 2026-06-10

Creates the users table — the canonical account record. Owns identity
(email + password hash), role, lifecycle status, and timestamps.
See app/models/user.py for the ORM mapping.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "instructor", "student", name="user_role"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "active", "suspended", name="user_status"
            ),
            nullable=False,
            server_default="pending",
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
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    # Drop the named enum types — only meaningful on Postgres; SQLite
    # stores enums as VARCHAR with a CHECK constraint that goes with the
    # table.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="user_role").drop(bind, checkfirst=False)
        sa.Enum(name="user_status").drop(bind, checkfirst=False)
