"""add name and phone columns to users

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-11

Adds two new columns to the users table for S7 (parent self-signup):
- name (NOT NULL, default '') — registered account holder's name.
- phone (nullable) — optional Nigerian contact number.

Both columns are added as nullable first so the migration is safe on
existing rows, then `name` is back-filled to '' and switched to NOT NULL
on Postgres (SQLite uses batch mode so the constraint is applied at
table-recreation time).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # render_as_batch in alembic/env.py makes this work on SQLite too.
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "name",
                sa.String(length=200),
                nullable=False,
                server_default="",
            )
        )
        batch_op.add_column(
            sa.Column("phone", sa.String(length=20), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("phone")
        batch_op.drop_column("name")
