"""VOREM AI Tutor — Agent A1 "Ada" (S23).

Implements the VOREM teaching loop:
  V — Verbalize: explain the concept clearly and simply.
  O — Observe:   end every reply with exactly one check question.
  R — Reflect:   adapt depth and language to the learner's level.
  E — Encourage: warm, positive, supportive tone throughout.
  M — Monitor:   stay strictly within the lesson content.

Security invariants:
  - The lesson body is injected as system-prompt context, not user
    content, so the learner cannot override the scope with a prompt.
  - answer_index is never present in the context passed to the model.
  - Output is returned verbatim here; the safety filter (S24) wraps
    this function at the API layer.

Every call produces one AgentRun row regardless of success or failure.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

import anthropic

from app.core.config import settings

AGENT_NAME = "tutor"

_SYSTEM_PROMPT_TEMPLATE = """\
You are Ada, the AI tutor for Treasured Child Academy, a K-12 school in Nigeria.
You are helping a student understand the lesson described below.

═══════════════════════════════
LESSON: {lesson_title}
COURSE: {course_title}  |  LEVEL: {course_level}
───────────────────────────────
{lesson_body}
═══════════════════════════════

TEACHING METHOD — VOREM:
1. Verbalize   — explain the concept clearly in simple, age-appropriate language.
2. Observe     — end your reply with EXACTLY ONE check question to confirm understanding.
3. Reflect     — adapt your explanation to a {course_level} student.
4. Encourage   — be warm, positive, and supportive.
5. Monitor     — stay strictly on the lesson content above.

STRICT RULES (non-negotiable):
• Only discuss topics in the lesson above. If asked about anything else, gently redirect.
• Never reveal quiz answers, exam answers, or grading criteria.
• Never ask for or accept personal contact details (phone, email, address, social media).
• If a student seems distressed or mentions harm, respond ONLY with:
  "I hear you. Please talk to a trusted adult at school or at home — they want to help you."
• Keep replies under 300 words unless the student explicitly asks for more detail.
• Use clear, friendly Nigerian-English suitable for a school student.\
"""


def build_system_prompt(lesson_context: Dict[str, Any]) -> str:
    return _SYSTEM_PROMPT_TEMPLATE.format(
        lesson_title=lesson_context["title"],
        course_title=lesson_context["course_title"],
        course_level=lesson_context["level"],
        lesson_body=lesson_context["body"] or "(No lesson content provided.)",
    )


def call_tutor(
    *,
    lesson_context: Dict[str, Any],
    question: str,
) -> Dict[str, Any]:
    """Call the Anthropic API with the VOREM system prompt.

    Returns:
        {
            "reply":  str,   # the model's text response
            "tokens": int,   # total tokens used (input + output)
        }

    Raises anthropic.APIError on API-level failures (caller handles).
    """
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    system_prompt = build_system_prompt(lesson_context)

    response = client.messages.create(
        model=settings.AGENT_MODEL,
        max_tokens=settings.AGENT_MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )

    reply = response.content[0].text if response.content else ""
    tokens = (
        response.usage.input_tokens + response.usage.output_tokens
        if response.usage
        else 0
    )

    return {"reply": reply, "tokens": tokens}
