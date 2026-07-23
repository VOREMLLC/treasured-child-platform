"""AgentRun model (S23).

Every call to any AI agent writes one row here before the reply is
returned. This provides an immutable audit trail, supports debugging,
and is the source of truth for `flagged` distress events (S24).

Fields:
  agent       — short name, e.g. "tutor".
  learner_id  — nullable FK to users.id (null for unauthenticated calls,
                though the tutor endpoint requires auth).
  input       — the full question/prompt as received by the agent.
  output      — the reply generated (or the safe-refusal message).
  tokens      — total tokens consumed by the API call.
  flagged     — True if the safety pipeline flagged this call (S24).
  created_at  — immutable timestamp.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    agent: Mapped[str] = mapped_column(Text, nullable=False)
    learner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    input: Mapped[str] = mapped_column(Text, nullable=False)
    output: Mapped[str] = mapped_column(Text, nullable=False)
    tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    flagged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
