# STRUCTURE.md — Folder, Environment & Architecture Map

## Folder layout
```
treasured-child-platform/
├── README.md            project overview + quickstart
├── CLAUDE.md            agent operating context (read first)
├── .env.example         env var names (no values)
├── docs/                PRD · URD · PWD · SDD · AGENTS · STRUCTURE
├── frontend/
│   ├── demo/index.html  clickable visual prototype (website + LMS)
│   └── src/             Next.js 14 app
│       ├── app/         routes (marketing + portals)
│       ├── components/  UI components
│       └── lib/         API client, auth, helpers
├── backend/
│   ├── app/             FastAPI: api/ models/ schemas/ services/ core/
│   └── agents/          agent runtime: runtime.py tools.py guardrails.py + one dir per agent
└── infra/               IaC, CI/CD config, migrations
```

## Environments
| Env | Frontend | Backend | DB | Purpose |
|---|---|---|---|---|
| dev | localhost:3000 | localhost:8000 | local Postgres | build/test |
| staging | Vercel preview | Railway staging | staging Postgres | QA + proprietor demo |
| prod | Vercel | Railway / Cloud Run | managed Postgres | live |

Promotion: PR → CI (lint+test) → merge `main` → auto-deploy. Migrations (Alembic) run on deploy.

## Architecture (one line)
Next.js (Vercel) → FastAPI (Railway/Cloud Run) → PostgreSQL + Redis, with a guarded Claude-powered agent runtime and Paystack for money. Determinism (money, grades, access) lives in code; language/judgement lives in agents. Full detail in `SDD.md` and `AGENTS.md`.
