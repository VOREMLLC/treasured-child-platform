"""quiz_attempts table (S21)

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-13

Stores every quiz submission. Re-attempts are allowed; no unique
constraint on (learner_id, quiz_id). xp_awarded is NULL until S22
wires gamification in.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("quiz_id", sa.Uuid(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("xp_awarded", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["quiz_id"], ["quizzes.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["learner_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_quiz_attempts_quiz_id", "quiz_attempts", ["quiz_id"]
    )
    op.create_index(
        "ix_quiz_attempts_learner_id", "quiz_attempts", ["learner_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_quiz_attempts_learner_id", table_name="quiz_attempts")
    op.drop_index("ix_quiz_attempts_quiz_id", table_name="quiz_attempts")
    op.drop_table("quiz_attempts")
