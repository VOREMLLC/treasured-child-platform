# AGENTS.md — Agentic AI Design
**Product:** Treasured Child Platform · Defines every AI agent: purpose, inputs, tools, outputs, guardrails.

## 0. Principle
> An agent is only as good as the **environment** built around it.

An "agent" here = **system prompt + scoped context + a permissioned set of tools + memory + guardrails**, run inside the agent runtime (`backend/agents/`). Agents never access the database directly; they call backend tools through a permissioned interface, and every run is logged to `AgentRun`. Input and output pass through a safety filter. The LMS must remain fully functional if the agent runtime is offline — agents augment, they are not load-bearing.

## 1. Agent roster

### A1 · AI Tutor ("Ada")
- **Purpose:** help a learner understand a concept in the current lesson — Socratic, encouraging, simple language.
- **Inputs:** lesson context, learner question, learner class level.
- **Tools:** `get_lesson_context`, `get_learner_progress` (read-only).
- **Output:** a short, age-appropriate explanation; never the quiz answer key.
- **Guardrails (mandatory):** learners are minors. Never produce romantic/sexual/unsafe content; never request personal contact info or arrange off-platform contact; refuse and escalate to a human on signs of distress or harm; stay on educational topic; no medical/legal advice. Output is filtered before display.

### A2 · Admissions Agent
- **Purpose:** answer prospective-parent questions, capture leads, suggest a visit.
- **Tools:** `get_programmes`, `get_fees`, `create_lead` (write to admin queue).
- **Output:** helpful answers + a captured lead. **Guardrail:** no payment handling; no promises on fees beyond published data.

### A3 · Curriculum Agent
- **Purpose:** draft lessons, summaries, and quizzes for a **teacher to review and approve** (human-in-the-loop; never auto-publishes).
- **Tools:** `get_course`, `propose_quiz` (draft only).
- **Guardrail:** curriculum-aligned; flagged for teacher approval before publish.

### A4 · Progress & Nudge Agent
- **Purpose:** turn learner data into parent-friendly progress summaries and gentle streak/lesson nudges.
- **Tools:** `get_learner_progress`, `send_notification` (templated, rate-limited).
- **Guardrail:** privacy-scoped to the guardian's own child; no comparative shaming.

### A5 · Growth/Content Agent (back-office)
- **Purpose:** draft marketing/social content for staff review.
- **Tools:** `get_results`, `get_events`.
- **Guardrail:** internal draft only; no claims unsupported by school data.

## 2. Orchestration
- Stateless request → runtime loads **only** the agent's allowed context + tools → Claude API (tool use loop) → tool calls validated against the agent's permissions → safety filter → response.
- **Memory:** short-term within a session (Redis); long-term limited to summaries tied to a learner/guardian, consent-gated.
- **Determinism where it matters:** scoring, payments, access-gating are **code**, not agents. Agents handle language and judgement, never money or grades-of-record.

## 3. Safety pipeline (every agent)
`input → policy filter → agent (scoped tools) → output filter → log(AgentRun) → deliver`
On any flag: block, log, and (for Tutor distress signals) surface a human-contact prompt.

## 4. Why this is the "right environment"
The model is fixed; the **environment** is the lever: correct context injection, least-privilege tools, human-in-the-loop on anything published or charged, hard-coded determinism for money/grades, and child-safety filters that cannot be prompted away. Build the environment right and a capable model produces safe, useful, accountable behaviour.
