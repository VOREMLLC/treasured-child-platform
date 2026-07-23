"""quizzes and questions tables (S20)

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-13

Quiz is one-to-one with Lesson (unique lesson_id). Question carries
answer_index which is intentionally absent from every Pydantic schema
— see app/models/quiz.py for the security rationale.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("lesson_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
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
            ["lesson_id"], ["lessons.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lesson_id", name="uq_quiz_lesson"),
    )
    op.create_index("ix_quizzes_lesson_id", "quizzes", ["lesson_id"])

    op.create_table(
        "questions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("quiz_id", sa.Uuid(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("answer_index", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["quiz_id"], ["quizzes.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_questions_quiz_id", "questions", ["quiz_id"])


def downgrade() -> None:
    op.drop_index("ix_questions_quiz_id", table_name="questions")
    op.drop_table("questions")
    op.drop_index("ix_quizzes_lesson_id", table_name="quizzes")
    op.drop_table("quizzes")
