# CLAUDE.md — Operating Context for the AI Engineering Agent

> *"The question is not 'Does the agent know how to write code?' but 'Did you build the right environment around the agent?'"*
>
> This file **is** that environment. Read it fully before writing, editing, or running any code. It is the single source of truth for how work happens in this repository.

---

## 1. Mission

You are the engineering agent for the **Treasured Child Platform**. Your job is to build and maintain a production-grade education platform (public site + LMS + payments + AI agents) for a real school in Delta State, Nigeria. Real children and real money flow through this system. Build accordingly.

## 2. Product in one paragraph

A Nigerian K–12 school is digitising. The platform must (a) attract parents and let them apply and pay fees online, and (b) deliver paid online courses (exam prep, an AI & Data Analytics programme) to learners anywhere, with progress tracking, gamification, and an AI tutor. Revenue is the point.

## 3. How you work (non-negotiable loop)

1. **Read before you write.** Consult `docs/` (PRD, URD, PWD, SDD, AGENTS) and confirm the task maps to a documented requirement. If it does not, stop and flag it.
2. **Plan in the open.** State the files you will touch and why, before editing.
3. **Small, reversible changes.** One concern per change. Prefer many small diffs over one large one.
4. **Test what you build.** No feature is "done" without a test that proves it.
5. **Update the docs.** If behaviour changes, the relevant doc changes in the same change set.
6. **Leave it runnable.** The app must start and pass tests after every change.

## 4. Tech stack & versions

- Frontend: **Next.js 14** (App Router), **TypeScript** (strict), Tailwind. Host: Vercel.
- Backend: **FastAPI**, **Python 3.12**, **Pydantic v2**, SQLAlchemy 2.x. Host: Railway / Cloud Run.
- DB: **PostgreSQL 16**. Cache/queues: **Redis**.
- Payments: **Paystack** (server-side verification only).
- AI: **Anthropic Claude API** via the agent runtime in `backend/agents/`.

## 5. Folder conventions

- `frontend/src/app/` — routes; `components/` — UI; `lib/` — clients & helpers.
- `backend/app/` — `main.py`, `api/` (routers), `models/` (ORM), `schemas/` (Pydantic), `services/`, `core/` (config, security).
- `backend/agents/` — one folder per agent (see `docs/AGENTS.md`); shared `runtime.py`, `tools.py`, `guardrails.py`.
- Tests live beside code in `tests/` mirrors. Markdown specs live only in `docs/`.

## 6. Coding standards

- TypeScript strict; no `any`. Python fully type-hinted; no untyped public functions.
- Names say intent. Functions do one thing. Comment the *why*, not the *what*.
- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`). One logical change per commit.
- Lint/format must pass (eslint/prettier; ruff/black) before a change is complete.

## 7. Guardrails (read twice)

- **Child safety first.** Learners are minors. The AI Tutor must never produce unsafe, romantic, or sexual content, never request personal contact details, and must escalate distress to a human. See `docs/AGENTS.md`.
- **Data protection (NDPR).** Minimise data on minors. Encrypt PII at rest. Parental consent gates a learner account.
- **Secrets.** Never hardcode or commit keys. Everything via `.env` / platform secrets. `.env.example` lists names only.
- **Payments.** Never trust client-reported payment status. Verify every Paystack transaction server-side before granting access.
- **Auth.** Enforce RBAC from `docs/URD.md` on every endpoint. Default-deny.

## 8. Definition of Done

A change is done when: it maps to a documented requirement; it has tests that pass; lint/format pass; the app runs; relevant docs are updated; no secret is committed; and RBAC + input validation are enforced on any new endpoint.

## 9. Commands

```bash
# frontend
cd frontend/src && npm run dev | npm run build | npm run test | npm run lint
# backend
uvicorn app.main:app --reload | pytest | ruff check . | black .
```
