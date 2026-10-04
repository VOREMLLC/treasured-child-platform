# Backend — Treasured Child platform

FastAPI + SQLAlchemy 2 + Alembic. Exposes the REST API consumed by the
Next.js frontend and houses the AI agent runtime (added in slice S23).

## Python version note

CLAUDE.md specifies Python 3.12 as the production target. Local
development on this machine uses **Python 3.9**, which is what is
installed system-wide. All pinned dependencies in
[`requirements.txt`](requirements.txt) support both. Switching to 3.12
when it is installed is a one-line change in the venv command — no code
changes required.

## Run locally

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Apply migrations (creates tables in SQLite at backend/local.db by default)
alembic upgrade head

# Insert demo course data (idempotent — re-runs are safe)
python -m scripts.seed_demo

# Start the dev server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open <http://127.0.0.1:8000/healthz>.

## Database

- **Local dev:** SQLite at `backend/local.db` (the default in
  [`app/core/config.py`](app/core/config.py); the file is git-ignored).
- **Production:** PostgreSQL 16. Set `DATABASE_URL` in `.env` to the
  Postgres connection string and run `alembic upgrade head`.

Models live under [`app/models/`](app/models/). Migrations live under
[`alembic/versions/`](alembic/versions/). The User model is defined in
slice S5; subsequent slices add courses, lessons, enrolments, etc.

## Tests

```bash
pytest
```

Pytest configuration lives in [`pytest.ini`](pytest.ini). Tests live
under [`tests/`](tests/) and mirror the structure of `app/`.

## Layout

```
backend/
├── requirements.txt         # pinned dependencies
├── pytest.ini               # pytest config
├── alembic.ini              # alembic config
├── alembic/                 # migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial_users.py
├── app/                     # FastAPI application
│   ├── main.py              # app entry point + /healthz
│   ├── core/                # config, security helpers
│   │   └── config.py
│   ├── db/                  # SQLAlchemy engine + session
│   │   └── session.py
│   └── models/              # ORM models
│       ├── base.py
│       └── user.py
└── tests/                   # pytest tests
    └── test_healthz.py
```

## Quality gates

Before committing any backend change:

```bash
pytest                       # all tests must pass
# (linters added in a later slice — ruff + black per CLAUDE.md)
```

See [`../HARDENING_RULES.md`](../HARDENING_RULES.md) for the full
checkpoint / change / test / commit loop.

## Deploy (Railway)

The repo is a monorepo, so the backend is its own Railway service.

1. New service from the GitHub repo. No Root Directory is needed: the root
   `Dockerfile` + `railway.json` build the backend, run `alembic upgrade head`
   as pre-deploy and healthcheck `/healthz`. (If Root Directory is set to
   `backend`, `backend/railway.json` gives the same result via Railpack.)
2. Add a **Postgres** service and set the backend variable
   `DATABASE_URL=${{Postgres.DATABASE_URL}}`. Railway's `postgresql://` URL is
   rewritten to the `postgresql+psycopg://` driver in `app/core/config.py`.
3. Set the remaining variables from the root `.env.example` (`JWT_SECRET`,
   Paystack keys, `ANTHROPIC_API_KEY`, `FRONTEND_URL`). `CORS_ORIGINS` must be
   JSON, e.g. `["https://treasuredchildschool.com"]`.
4. Generate a public domain under **Settings → Networking**.

Without `DATABASE_URL` the app falls back to SQLite on the container disk,
which is wiped on every redeploy.
