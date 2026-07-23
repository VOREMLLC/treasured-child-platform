"""Gamification model (S22).

One row per learner. XP, level, streak, and badges are all stored here
and updated atomically through the gamification service.

Rules (from BUILD_SPEC §8):
  - Lesson complete → +20 XP (idempotent — once per unique lesson).
  - Quiz           → +15 XP × correct answers + 30 bonus if perfect.
  - Level          → floor(total_xp / 300) + 1.
  - Streak         → last_active_date yesterday → streak+1; today → unchanged; else reset to 1.
  - Badges (idempotent): First Lesson, 7-Day Streak, Quiz Master, Course Complete.

XP re-attempt rule: first-attempt-only for quiz XP (XP awarded only on
the learner's first attempt at a given quiz — see gamification service).
"""

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Gamification(Base):
    __tablename__ = "gamification"

    # One row per learner — learner_id IS the primary key (no separate id).
    learner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_active_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # JSON list of badge name strings — e.g. ["First Lesson", "Quiz Master"]
    badges: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )
