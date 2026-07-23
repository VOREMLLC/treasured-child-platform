"""gamification table (S22)

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-13

One row per learner (learner_id is the primary key). Stores XP, level,
streak, last_active_date, and a JSON badge list. Updated by the
gamification service whenever a lesson is completed or a quiz attempt
is scored.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gamification",
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_active_date", sa.Date(), nullable=True),
        sa.Column("badges", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["learner_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("learner_id"),
    )


def downgrade() -> None:
    op.drop_table("gamification")
