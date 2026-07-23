"""certificates table (S27)

Revision ID: 0014
Revises: 0013
Create Date: 2026-06-14

One row per (learner, course) pair. Unique constraint enforces
idempotent issuance — completing a course twice never yields two certs.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "certificates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["learner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "learner_id", "course_id", name="uq_certificate_learner_course"
        ),
    )
    op.create_index("ix_certificates_learner_id", "certificates", ["learner_id"])
    op.create_index("ix_certificates_course_id", "certificates", ["course_id"])


def downgrade() -> None:
    op.drop_index("ix_certificates_course_id", table_name="certificates")
    op.drop_index("ix_certificates_learner_id", table_name="certificates")
    op.drop_table("certificates")
