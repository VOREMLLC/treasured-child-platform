"""lesson_progress table

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-11

The canonical 'has the learner completed this lesson?' table. The
unique (learner_id, lesson_id) constraint is the DB-level idempotency
guarantee for POST /lessons/{id}/complete (S17).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["learner_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"], ["lessons.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id",
            "lesson_id",
            name="uq_lesson_progress_learner_lesson",
        ),
    )
    op.create_index(
        "ix_lesson_progress_learner_id",
        "lesson_progress",
        ["learner_id"],
    )
    op.create_index(
        "ix_lesson_progress_lesson_id",
        "lesson_progress",
        ["lesson_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lesson_progress_lesson_id", table_name="lesson_progress"
    )
    op.drop_index(
        "ix_lesson_progress_learner_id", table_name="lesson_progress"
    )
    op.drop_table("lesson_progress")
