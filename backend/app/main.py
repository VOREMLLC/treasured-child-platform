"""FastAPI application entry point.

Boots the app, wires up CORS (so the Next.js dev server on :3000 can
call the backend on :8000), wires up the shared rate limiter, and
registers every router. ``GET /healthz`` is exposed directly here as a
trivial liveness probe.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import applications, auth
from app.core.config import settings
from app.core.rate_limit import limiter

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


@app.get("/healthz")
def healthz() -> dict:
    """Liveness probe.

    Returns ``{"ok": true}`` if the process is running. Used by uptime
    monitoring and by automated tests as a smoke check.
    """
    return {"ok": True}
