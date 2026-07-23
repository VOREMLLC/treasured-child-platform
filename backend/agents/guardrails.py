"""Child-safety guardrails for the VOREM tutor (S24).

Two deterministic filter passes wrap every tutor call:

  1. INPUT FILTER  — runs before the LLM is called.
     Detects: distress signals, banned topics, PII solicitation.
     On hit: returns a safe reply immediately; LLM is never called.

  2. OUTPUT FILTER — runs after the LLM reply is received.
     Detects: unsafe / romantic / sexual content, off-platform contact
              solicitation in the model's output.
     On hit: replaces the reply with a safe refusal; flags the run.

Why deterministic code instead of a second LLM call?
  Safety filters must be prompt-injection resistant. A clever input can
  make an LLM-based filter approve itself. Keyword/pattern matching
  cannot be talked out of its rules (AGENTS.md §4 — "filters that
  cannot be prompted away").

Design contract:
  - check_input(question)  → InputCheckResult
  - check_output(reply)    → OutputCheckResult
  Both functions are pure (no side effects, no DB, no network).
  The endpoint caller decides what to log.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Safe reply messages
# ─────────────────────────────────────────────────────────────

SAFE_DISTRESS_REPLY = (
    "I hear you. Please talk to a trusted adult at school or at home — "
    "they want to help you. You can speak to your teacher, school counsellor, "
    "or a family member you trust."
)

SAFE_TOPIC_REFUSAL = (
    "I'm here to help with your school lessons. That topic is outside "
    "what I can discuss. Let's get back to your lesson — what would you "
    "like me to explain?"
)

SAFE_OUTPUT_REFUSAL = (
    "I'm sorry, I can't help with that. Let's focus on your lesson. "
    "What part of the topic would you like me to explain?"
)

# ─────────────────────────────────────────────────────────────
# Pattern lists
# ─────────────────────────────────────────────────────────────

# Distress: self-harm, abuse, bullying, suicidal ideation.
# Phrases that, if present, warrant immediate human escalation.
_DISTRESS_PHRASES: list[str] = [
    "want to die",
    "kill myself",
    "hurt myself",
    "hurting myself",
    "harm myself",
    "harming myself",
    "end my life",
    "suicide",
    "nobody cares about me",
    "i hate myself",
    "being abused",
    "someone is hurting me",
    "someone hurts me",
    "being bullied",
    "they hit me",
    "they touch me",
    "scared to go home",
    "feel like giving up",
    "don't want to live",
    "feel hopeless",
    "help me i'm scared",
]

# Banned input topics: sexual, violent, dangerous content, illegal.
# The learner must not route these questions through the tutor at all.
_BANNED_INPUT_PATTERNS: list[str] = [
    r"\bporn\b",
    r"\bsex\b",
    r"\bnaked\b",
    r"\bnude\b",
    r"\bdrug[s]?\b",
    r"\bcocaine\b",
    r"\bheroin\b",
    r"\bhow to make a bomb\b",
    r"\bhow to make bomb\b",
    r"\bexplosive\b",
    r"\bgun\b",
    r"\bweapon\b",
    r"\bhacking?\b",
    r"\bterror\b",
    r"\bkill (?:someone|a person|people)\b",
]

# PII solicitation: learner asking the tutor for contact details.
# Ada must never give out phone numbers, emails, or arrange off-platform contact.
_PII_REQUEST_PATTERNS: list[str] = [
    r"your (?:phone|number|mobile|cell)",
    r"your (?:email|address|location)",
    r"where (?:do you|are you) (?:live|from|located)",
    r"give me your (?:number|contact|details)",
    r"can (?:we|i) (?:chat|talk|meet) (?:outside|off|privately)",
    r"whatsapp",
    r"instagram",
    r"facebook",
    r"snapchat",
    r"tiktok",
    r"add me on",
    r"follow me on",
]

# Unsafe output: sexual/romantic content or contact solicitation in LLM reply.
_UNSAFE_OUTPUT_PATTERNS: list[str] = [
    r"\bmy (?:phone|number|mobile|cell) (?:is|number)\b",
    r"\bmy email is\b",
    r"\bcall me at\b",
    r"\btext me\b",
    r"\bmeet me\b",
    r"\bsex\b",
    r"\bporn\b",
    r"\bnaked\b",
    r"\bnude\b",
    r"\bexplicit\b",
    r"\berotica\b",
    r"\bromantic\b.*\bkiss\b",
    r"\bkiss\b.*\bromantic\b",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, lower):
            return True
    return False


def _contains_distress(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in _DISTRESS_PHRASES)


# ─────────────────────────────────────────────────────────────
# Public result types
# ─────────────────────────────────────────────────────────────


@dataclass
class InputCheckResult:
    """Outcome of the input policy filter."""

    blocked: bool
    distress: bool          # subset of blocked; triggers flagged=True in DB
    safe_reply: Optional[str]  # non-None when blocked is True


@dataclass
class OutputCheckResult:
    """Outcome of the output policy filter."""

    blocked: bool   # True → output was replaced
    reply: str      # final reply (original or replacement)


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────


def check_input(question: str) -> InputCheckResult:
    """Apply the input policy filter to a learner's question.

    Priority order:
      1. Distress signals   → SAFE_DISTRESS_REPLY, distress=True.
      2. Banned topics      → SAFE_TOPIC_REFUSAL,  distress=False.
      3. PII solicitation   → SAFE_TOPIC_REFUSAL,  distress=False.

    Returns an unblocked result if none match.
    """
    if _contains_distress(question):
        return InputCheckResult(
            blocked=True,
            distress=True,
            safe_reply=SAFE_DISTRESS_REPLY,
        )
    if _matches_any(question, _BANNED_INPUT_PATTERNS):
        return InputCheckResult(
            blocked=True,
            distress=False,
            safe_reply=SAFE_TOPIC_REFUSAL,
        )
    if _matches_any(question, _PII_REQUEST_PATTERNS):
        return InputCheckResult(
            blocked=True,
            distress=False,
            safe_reply=SAFE_TOPIC_REFUSAL,
        )
    return InputCheckResult(blocked=False, distress=False, safe_reply=None)


def check_output(reply: str) -> OutputCheckResult:
    """Apply the output policy filter to the LLM's reply.

    If the reply contains unsafe content, replace it with SAFE_OUTPUT_REFUSAL.
    """
    if _matches_any(reply, _UNSAFE_OUTPUT_PATTERNS):
        return OutputCheckResult(blocked=True, reply=SAFE_OUTPUT_REFUSAL)
    return OutputCheckResult(blocked=False, reply=reply)
