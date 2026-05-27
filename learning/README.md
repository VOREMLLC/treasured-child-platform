# `learning/` — the VOREM agentic education system

## What it does
This is **the heart of the LMS**. Three concerns live together here
because they are inseparable on every learner interaction:

1. **Lesson progress.** Records when a learner completes a lesson; recomputes course progress. One source of truth for every progress number anywhere on the platform.
2. **Gamification.** XP per action, levels, daily streaks, badges. All idempotent — the same action never awards twice.
3. **The VOREM tutor.** The in-lesson AI that follows the pedagogy loop: **explain the concept simply → check the learner understood with one question → adapt to the learner's level → encourage and track progress.** Every reply passes through the **child-safety guardrails** defined alongside it.

## What goes in (input)
- A learner's "mark complete" action on a lesson.
- A learner's question to the tutor inside an open lesson (`POST /agents/tutor {lesson_id, question}`).
- A correct quiz answer or perfect quiz from [`assessment/`](../assessment/) — used to award XP / badges.

## What comes out (output)
- A `lesson_progress` row (unique on `(learner_id, lesson_id)`).
- An updated `gamification` row for the learner.
- A tutor reply that is on-topic, age-appropriate, and safe. The reply is bound to the current `lesson_id`; the tutor does not free-roam to other topics.
- An `agent_runs` log entry for every tutor call (with `flagged=true` set on distress / unsafe triggers).

## Owns these v1 features
17. VOREM agentic lesson tutor · 18. Lesson progress tracking ·
19. Child-safety guardrails on AI replies · 22. XP, levels, streaks,
badges.

## Build slices
S17 (lesson complete + progress), S22 (gamification), S23 (tutor MVP),
S24 (safety guardrails).

## What does **not** belong here
- Course / lesson **content** itself — that's in [`courses/`](../courses/).
- Quiz scoring — that's in [`assessment/`](../assessment/). Awarding XP **after** a quiz is `learning/`'s job; computing the score is not.
- Certificates — those are in [`certificates/`](../certificates/), triggered when `learning/` reports `course_progress == 100%`.

## Safety rules that apply here (the most important in the codebase)
- **The tutor never produces unsafe, romantic, or sexual content.** Output filter blocks; reply is replaced with a safe redirect.
- **The tutor never asks for personal contact details.** Input filter recognises and refuses.
- **Distress signals trigger a human-contact prompt** and set `agent_runs.flagged=true` for admin review.
- **The tutor never sees other learners' data.** It is scoped to the current lesson and the current learner.
- **Money, grades and access decisions are never made by the agent.** Those paths are code-only.
