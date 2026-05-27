# Treasured Child Platform

A two-engine education platform for **Treasured Child Nursery, Primary & Secondary School, Orerokpe (Delta State, Nigeria)**:

1. **Brand & Admissions site** — a public website that grows enrolment and collects fees online.
2. **Learning Management System (LMS)** — a digital learning experience with paid online programmes (exam prep, an AI & Data Analytics course), gamification, and an agentic **AI Tutor**.

The platform turns the school's strong reputation into scalable, measurable revenue — both by lifting physical enrolment and by selling education beyond the school's walls.

---

## Tech stack

| Layer | Technology | Host |
|---|---|---|
| Frontend | Next.js 14 (App Router), React, TypeScript | Vercel |
| Backend API | FastAPI (Python 3.12), Pydantic v2 | Railway / Google Cloud Run |
| Database | PostgreSQL 16 | Managed (Railway/Supabase) |
| Cache / queues | Redis | Managed |
| Payments | Paystack | — |
| AI agents | Anthropic Claude API (tool use) | Backend runtime |
| Auth | JWT (access + refresh), RBAC | — |

> The `frontend/demo/index.html` file is a **self-contained clickable prototype** of both the website and the LMS. It is the visual proof-of-concept and is deployable to Vercel as a static page as-is. Production is built to the stack above.

## Repository structure

```
tc/
├── README.md            ← you are here
├── CLAUDE.md            ← operating context for the AI engineering agent
├── .env.example         ← required environment variables
├── docs/
│   ├── PRD.md           ← Product Requirements Document
│   ├── URD.md           ← User Role Document (RBAC)
│   ├── PWD.md           ← Product Work Document (delivery plan)
│   ├── SDD.md           ← System Design Document (architecture + data model)
│   ├── AGENTS.md        ← Agentic AI design (the platform's AI agents)
│   └── STRUCTURE.md     ← folder + environment + architecture map
├── frontend/
│   ├── demo/index.html  ← the visual prototype (open in a browser)
│   └── src/             ← production Next.js app
└── backend/
    ├── app/             ← FastAPI application
    └── agents/          ← AI agent runtime + tools
```

## Quickstart

```bash
# 1. View the prototype
open frontend/demo/index.html

# 2. Frontend (production)
cd frontend/src && npm install && npm run dev

# 3. Backend (production)
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && uvicorn app.main:app --reload

# 4. Environment
cp .env.example .env   # fill in keys (never commit .env)
```

## Where to start
Read the docs in this order: **PRD → URD → PWD → SDD → AGENTS**. Then read `CLAUDE.md` before writing any code.
