"""FastAPI application entry point.

Boots the app, wires up CORS (so the Next.js dev server on :3000 can
call the backend on :8000), wires up the shared rate limiter, and
registers every router. ``GET /healthz`` is exposed directly here as a
trivial liveness probe.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import admin, agents, applications, auth, courses, enrolments, me, payments, quizzes
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db

app = FastAPI(
    title="Treasured Child Platform — Backend",
    version="0.1.0",
    description=(
        "REST API for the Treasured Child website + LMS. See "
        "docs/PRODUCT_REQUIREMENTS.md and docs/BUILD_PLAN.md."
    ),
)

# CORS — the Next.js dev server lives on a different origin from the
# backend, so the browser will pre-flight every POST.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiter — register the shared Limiter on app.state and hook the
# exception handler so any @limiter.limit(...) decorator anywhere in the
# app produces a proper 429 response.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(applications.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(me.router)
app.include_router(payments.router)
app.include_router(enrolments.router)
app.include_router(quizzes.router)
app.include_router(courses.router)
app.include_router(agents.router)


@app.get("/healthz")
def healthz() -> dict:
    """Liveness probe.

    Returns ``{"ok": true}`` if the process is running. Used by uptime
    monitoring and by automated tests as a smoke check.
    """
    return {"ok": True}


@app.get("/readyz")
def readyz(db: Session = Depends(get_db)) -> dict:
    """Readiness probe: proves the database is reachable.

    Railway's deploy healthcheck uses this, so a deploy with a missing or
    broken ``DATABASE_URL`` never replaces a working one.
    """
    db.execute(text("SELECT 1"))
    return {"ok": True}
