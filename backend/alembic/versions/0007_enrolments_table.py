"""enrolments table

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-11

Lands the enrolments table so the catalogue / detail endpoints in S15
have something to query. POST /enrolments (S18) and payment-gated
paid enrolment (S19) reuse this schema.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enrolments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "expired", name="enrolment_status"),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "source",
            sa.Enum("free", "paid", name="enrolment_source"),
            nullable=False,
        ),
        sa.Column(
            "access_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
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
        sa.ForeignKeyConstraint(
            ["learner_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id", "course_id",
            name="uq_enrolment_learner_course",
        ),
    )
    op.create_index(
        "ix_enrolments_learner_id", "enrolments", ["learner_id"]
    )
    op.create_index(
        "ix_enrolments_course_id", "enrolments", ["course_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_enrolments_course_id", table_name="enrolments")
    op.drop_index("ix_enrolments_learner_id", table_name="enrolments")
    op.drop_table("enrolments")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="enrolment_status").drop(bind, checkfirst=False)
        sa.Enum(name="enrolment_source").drop(bind, checkfirst=False)
