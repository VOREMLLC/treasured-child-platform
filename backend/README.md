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

One Railway project, three services: **Postgres**, **backend** (repo root),
**website** (Root Directory `frontend`). The browser only talks to the
website; it proxies `/api/*` to the backend, so auth cookies are
first-party and no CORS setup is needed.

Backend service (no Root Directory; root `Dockerfile` + `railway.json`):

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` (enables Secure cookies; refuses placeholder secrets/SQLite) |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `JWT_SECRET` | 32+ random characters |
| `PAYSTACK_SECRET_KEY` / `PAYSTACK_PUBLIC_KEY` | live keys from the Paystack dashboard |
| `ANTHROPIC_API_KEY` | tutor key |
| `FRONTEND_URL` | website URL (used in reset emails) |
| `BOOTSTRAP_ADMIN_EMAIL` / `BOOTSTRAP_ADMIN_PASSWORD` | first admin, created once on deploy (12+ char password) |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `EMAIL_FROM` | any SMTP mailbox (e.g. the school's cPanel `admissions@` box: host `mail.<domain>`, port 465). Unset = no email in production |
| `ADMIN_EMAIL` | admissions inbox for new-application alerts |
| `SAFEGUARDING_EMAIL` | alerted when the AI tutor detects distress (falls back to `ADMIN_EMAIL`); messages are listed at `GET /admin/flagged-runs` |

Each start runs `alembic upgrade head` then `scripts.bootstrap_admin` (both idempotent) before uvicorn.
The healthcheck is `/readyz`, which queries the database, so a deploy
with a broken database never replaces a working one.

Website service: Root Directory `frontend`, variable
`BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}` (read at build
time; redeploy the website if it changes).

Paystack dashboard → Settings → API Keys & Webhooks: set the webhook URL
to `https://<backend-domain>/payments/webhook/paystack`.
