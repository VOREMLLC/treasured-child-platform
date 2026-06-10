"""Tests for the /healthz liveness probe."""

from fastapi.testclient import TestClient

from app.main import app


def test_healthz_returns_ok_true():
    """GET /healthz must return HTTP 200 with the body ``{"ok": true}``."""
    client = TestClient(app)
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
