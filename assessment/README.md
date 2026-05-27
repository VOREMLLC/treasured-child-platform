# `assessment/` — quizzes and server-side scoring

## What it does
Stores quizzes attached to lessons, serves quiz questions to enrolled
students, and **scores quiz attempts on the server**. Answer keys never
leave the backend.

## What goes in (input)
- A signed-in, enrolled student opens a quiz (`GET /quizzes/{id}`).
- A student submits an attempt (`POST /quizzes/{id}/attempt {answers: [index]}`).

## What comes out (output)
- A quiz payload containing only `{title, questions:[{id, prompt, options}]}` — the `answer_index` field is **never** in the response.
- A server-computed `{score, total, xp_awarded?, badge?}` on attempt submission.
- A persisted `attempts` row for audit and future analytics.

## Owns these v1 features
20. Quiz at end of a lesson · 21. Quiz attempt with server-side scoring.

## Build slices
S20 (model + read endpoint), S21 (attempt + scoring).

## What does **not** belong here
- XP / badge **rules** — those live in [`learning/`](../learning/). `assessment/` reports the result; `learning/` decides the reward.
- Lesson / course content — that's in [`courses/`](../courses/).
- The grading queue for instructor-marked items — that's "later" (instructor authoring is a future module surface).

## Safety rules that apply here
- **`Question.answer_index` is server-only.** It is never serialised into any Pydantic response schema. There is a test (`assessment/tests/`) that asserts this.
- **The score is computed server-side.** A client-claimed score in the request body is ignored.
- **Attempts are stored**, even failed ones, so a future complaint about a grade can be reconstructed.
