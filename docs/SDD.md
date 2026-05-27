# SDD — System Design Document
**Product:** Treasured Child Platform · Defines architecture, data, APIs, the agentic AI subsystem, security, and deployment.

## 1. Architecture overview

```
                         ┌──────────────────────────┐
        Browser ───────► │  Next.js 14 (Vercel)     │  public site + portals (SSR/CSR)
                         └────────────┬─────────────┘
                                      │ HTTPS / JSON (JWT)
                         ┌────────────▼─────────────┐
                         │  FastAPI (Railway/Cloud   │
                         │  Run)  — REST API + RBAC  │
                         └──┬────────┬────────┬──────┘
                            │        │        │
        ┌───────────────────▼─┐  ┌───▼────┐  ┌▼───────────────┐
        │ PostgreSQL 16        │  │ Redis  │  │ Agent Runtime  │
        │ (users, courses,     │  │ cache, │  │ (Claude API +  │
        │  payments, attempts) │  │ jobs   │  │  tools+guards) │
        └──────────────────────┘  └────────┘  └───┬────────────┘
                                                   │
                          ┌────────────────────────┼─────────────┐
                          ▼                         ▼             ▼
                     Paystack API            Object storage   Email/SMS
                  (fees, programmes)        (media, content)   (notices)
```

## 2. Components
- **Frontend (Next.js):** marketing pages (static/ISR for SEO), authenticated portals (learner/parent/teacher/admin), Paystack inline checkout, calls backend via typed API client.
- **Backend (FastAPI):** REST API, JWT auth, RBAC middleware, payment verification, LMS logic, orchestrates the agent runtime.
- **PostgreSQL:** system of record. **Redis:** sessions/cache, rate limiting, background job queue.
- **Agent runtime:** isolated service that runs AI agents with tools, memory, and guardrails (see `AGENTS.md`).
- **Integrations:** Paystack (payments), object storage (lesson media), email/SMS (notifications).

## 3. Core data model (key entities)

| Entity | Key fields | Notes |
|---|---|---|
| `User` | id, email, password_hash, role, status | RBAC role from URD |
| `Learner` | id, user_id, dob, class_level, guardian_id, consent | minor; consent-gated |
| `Guardian` | id, user_id, phone | parent account |
| `Course` | id, title, type (school/online), level, is_paid, price_kobo | online = nationally sellable |
| `Module` / `Lesson` | id, course_id, order, title, content, media_url | lesson belongs to module |
| `Enrolment` | id, learner_id, course_id, status, access_expires_at | gates paid access |
| `Quiz` / `Question` | id, lesson_id, type, options, answer_key | answer_key never sent to client |
| `Attempt` | id, learner_id, quiz_id, score, answers, taken_at | scoring server-side |
| `Payment` | id, payer_id, ref, amount_kobo, purpose, status, verified_at | Paystack ref + server verify |
| `Subscription` | id, payer_id, plan, status, renews_at | Phase 3 |
| `Gamification` | learner_id, xp, level, streak, badges[] | engagement |
| `AgentRun` | id, agent, input, output, tokens, flagged | audit of every agent call |
| `AuditLog` | id, actor, action, target, ts | sensitive actions |

Money stored in **kobo** (integers) to avoid float errors.

## 4. API surface (representative)
```
POST /auth/register            POST /auth/login            POST /auth/refresh
POST /applications             GET  /admin/applications
POST /payments/initialize      POST /payments/verify       (server-side Paystack verify)
GET  /courses                  GET  /courses/{id}
GET  /lessons/{id}             POST /lessons/{id}/complete
POST /quizzes/{id}/attempt     (returns score; answer_key withheld)
POST /enrolments               (created only after payment verified, if paid)
POST /agents/tutor             POST /agents/admissions     (rate-limited, guarded)
GET  /me/dashboard             GET  /reports/kpis          (RBAC: admin/proprietor)
```
Every endpoint: validate input (Pydantic), enforce RBAC + ownership, audit sensitive actions.

## 5. Agentic AI subsystem (summary; full spec in AGENTS.md)
Each agent = **system prompt + allowed tools + scoped memory + guardrails**, executed in the agent runtime. The runtime injects only the context an agent needs (the "environment around the agent"), logs every run to `AgentRun`, and applies a safety filter on input and output. Agents call backend tools through a permissioned interface — they never touch the database directly.

## 6. Security & compliance
- **AuthN/Z:** hashed passwords (argon2), JWT, default-deny RBAC, ownership checks.
- **Minors (NDPR):** data minimisation, PII encryption at rest, parental consent to activate a learner, child-safety guardrails on the Tutor.
- **Payments:** server-side verification only; idempotent webhooks; never gate access on client claims.
- **Secrets:** environment variables / platform secret stores; nothing in the repo.
- **Observability:** structured logs, request tracing, `AgentRun` + `AuditLog` for accountability.

## 7. Environments & deployment
`dev` (local) → `staging` (Vercel preview + Railway staging) → `prod`. CI: lint + tests on every PR; CD: auto-deploy frontend (Vercel) and backend (Railway/Cloud Run) on merge to `main`. Database migrations via Alembic, run on deploy.

## 8. Non-functional targets
First-contentful paint < 2s on 3G for marketing pages; API p95 < 300ms (non-AI); AI tutor response < 6s; horizontal scale on the backend; graceful degradation if the agent runtime is unavailable (LMS still works without AI).
