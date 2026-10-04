"""Agent endpoints (S23 + S24).

  POST /agents/tutor   Auth + enrolment-gated VOREM tutor call.

Full safety pipeline (AGENTS.md §3):
  input → guardrails.check_input → [LLM call] → guardrails.check_output
  → log(AgentRun) → deliver

S24 additions over S23:
  - Input policy filter (distress, banned topics, PII requests) applied
    before the LLM is called. Blocked inputs short-circuit and return a
    safe reply immediately; the LLM is never invoked.
  - Output policy filter applied to the LLM reply before it is returned.
    Unsafe output is replaced with a safe refusal.
  - Both distress signals and unsafe output set AgentRun.flagged=True.
  - Rate limit: 20 requests / minute per learner (slowapi).

LMS resilience rule (AGENTS.md §0):
  If the Anthropic API is unavailable the endpoint returns 503 with a
  user-friendly message — the rest of the LMS continues to function.
"""

import uuid

import anthropic
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agents import tutor as tutor_agent
from agents.guardrails import check_input, check_output
from agents.tools import get_lesson_context
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.agent_run import AgentRun
from app.models.course import Lesson, Module
from app.models.enrolment import Enrolment, EnrolmentStatus
from app.models.user import User
from app.services import email as email_service

router = APIRouter(prefix="/agents", tags=["agents"])

_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Forbidden.",
)


# ─────────────────────────────────────────────────────────────
# Request / response shapes
# ─────────────────────────────────────────────────────────────


class TutorRequest(BaseModel):
    lesson_id: uuid.UUID
    question: str = Field(..., min_length=1, max_length=2000)


class TutorResponse(BaseModel):
    reply: str
    run_id: uuid.UUID


# ─────────────────────────────────────────────────────────────
# Enrolment gate helper
# ─────────────────────────────────────────────────────────────


def _assert_enrolled(
    lesson_id: uuid.UUID, user: User, db: Session
) -> None:
    """Raise 403 if the user is not actively enrolled in this lesson's course."""
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise _FORBIDDEN
    module = db.get(Module, lesson.module_id)
    if module is None:
        raise _FORBIDDEN
    enrolment = (
        db.query(Enrolment)
        .filter(Enrolment.learner_id == user.id)
        .filter(Enrolment.course_id == module.course_id)
        .filter(Enrolment.status == EnrolmentStatus.active)
        .first()
    )
    if enrolment is None:
        raise _FORBIDDEN


# ─────────────────────────────────────────────────────────────
# POST /agents/tutor
# ─────────────────────────────────────────────────────────────


@router.post("/tutor", response_model=TutorResponse, status_code=200)
@limiter.limit("20/minute")
def ask_tutor(
    request: Request,  # noqa: ARG001  # required by slowapi for IP key
    payload: TutorRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TutorResponse:
    """Ask Ada a question about a specific lesson.

    Safety pipeline (S24):
      1. Enrolment gate — 403 if not enrolled.
      2. Input filter   — distress/banned/PII → safe reply, flagged=True, no LLM call.
      3. LLM call       — Anthropic API (503 on failure).
      4. Output filter  — unsafe output replaced with safe reply, flagged=True.
      5. AgentRun log   — every call logged regardless of outcome.
    """
    _assert_enrolled(payload.lesson_id, current_user, db)

    lesson_context = get_lesson_context(payload.lesson_id, db)
    assert lesson_context is not None  # guaranteed by enrolment check above

    # ── 1. Input policy filter ──────────────────────────────
    input_result = check_input(payload.question)
    if input_result.blocked:
        run = _log_run(
            db,
            learner_id=current_user.id,
            input_text=payload.question,
            output_text=input_result.safe_reply or "",
            tokens=0,
            flagged=input_result.distress,  # distress=True sets flagged
        )
        if input_result.distress:
            _alert_safeguarding(run, current_user)
        return TutorResponse(reply=input_result.safe_reply or "", run_id=run.id)

    # ── 2. LLM call ─────────────────────────────────────────
    reply_text = ""
    tokens = 0
    try:
        result = tutor_agent.call_tutor(
            lesson_context=lesson_context,
            question=payload.question,
        )
        reply_text = result["reply"]
        tokens = result["tokens"]
    except anthropic.APIError as exc:
        _log_run(
            db,
            learner_id=current_user.id,
            input_text=payload.question,
            output_text="",
            tokens=0,
            flagged=False,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The AI tutor is temporarily unavailable. "
                "Please try again in a moment."
            ),
        ) from exc

    # ── 3. Output policy filter ─────────────────────────────
    output_result = check_output(reply_text)

    run = _log_run(
        db,
        learner_id=current_user.id,
        input_text=payload.question,
        output_text=output_result.reply,
        tokens=tokens,
        flagged=output_result.blocked,
    )

    return TutorResponse(reply=output_result.reply, run_id=run.id)


def _alert_safeguarding(run: AgentRun, learner: User) -> None:
    """Tell a human straight away that a learner may be in distress.

    CLAUDE.md §7: distress must escalate to a person, not just a DB flag.
    The child's words stay in the database (admin: GET /admin/flagged-runs);
    the email carries only what the safeguarding lead needs to act.
    """
    to = settings.SAFEGUARDING_EMAIL or settings.ADMIN_EMAIL
    print(f"[safeguarding] distress flagged run={run.id}", flush=True)
    email_service.send_email(
        to=to,
        subject="Safeguarding alert: a learner may need help",
        body=(
            "The AI tutor detected a message suggesting a learner may be in "
            "distress. Please follow up today.\n\n"
            f"Learner: {learner.name or '(no name)'} <{learner.email}>\n"
            f"Flagged at: {run.created_at:%d %b %Y, %H:%M} UTC\n"
            f"Reference: {run.id}\n\n"
            "Sign in as an admin to read the message (GET /admin/flagged-runs)."
        ),
    )


def _log_run(
    db: Session,
    *,
    learner_id: uuid.UUID,
    input_text: str,
    output_text: str,
    tokens: int,
    flagged: bool,
) -> AgentRun:
    run = AgentRun(
        agent=tutor_agent.AGENT_NAME,
        learner_id=learner_id,
        input=input_text,
        output=output_text,
        tokens=tokens,
        flagged=flagged,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
