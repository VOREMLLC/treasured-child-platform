"""agent_runs table (S23)

Revision ID: 0012
Revises: 0011
Create Date: 2026-06-13

Immutable audit log for every AI agent call. Flagged column (S24) starts
as false; the safety pipeline sets it to true on distress/policy events.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("agent", sa.Text(), nullable=False),
        sa.Column("learner_id", sa.Uuid(), nullable=True),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("output", sa.Text(), nullable=False),
        sa.Column("tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("flagged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["learner_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_runs_learner_id", "agent_runs", ["learner_id"])


def downgrade() -> None:
    op.drop_index("ix_agent_runs_learner_id", table_name="agent_runs")
    op.drop_table("agent_runs")
