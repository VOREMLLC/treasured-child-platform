"""FastAPI application entry point.

Boots the app and exposes a /healthz liveness endpoint. Every other
route gets registered by the routers under app/api/ as later slices
add features.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Treasured Child Platform — Backend",
    version="0.1.0",
    description=(
        "REST API for the Treasured Child website + LMS. See "
        "docs/PRODUCT_REQUIREMENTS.md and docs/BUILD_PLAN.md."
    ),
)


@app.get("/healthz")
def healthz() -> dict:
    """Liveness probe.

    Returns ``{"ok": true}`` if the process is running. Used by uptime
    monitoring and by automated tests as a smoke check.
    """
    return {"ok": True}
