"""Tests for production-deploy safeguards."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from starlette.requests import Request

from app.core.config import Settings
from app.core.rate_limit import client_ip
from app.models.user import User, UserRole, UserStatus
from scripts.bootstrap_admin import bootstrap_admin

SAFE_PROD = {
    "ENVIRONMENT": "production",
    "DATABASE_URL": "postgresql://u:p@host/db",
    "JWT_SECRET": "x" * 40,
    "PAYSTACK_SECRET_KEY": "sk_live_real",
}


def test_safe_production_config_boots() -> None:
    settings = Settings(**SAFE_PROD)
    assert settings.is_production


@pytest.mark.parametrize(
    "override",
    [
        {"DATABASE_URL": "sqlite:///./local.db"},
        {"JWT_SECRET": "change-me-in-production"},
        {"JWT_SECRET": "too-short"},
        {"PAYSTACK_SECRET_KEY": "sk_test_xxx"},
    ],
)
def test_unsafe_production_config_refuses_to_boot(override: dict) -> None:
    with pytest.raises(ValidationError):
        Settings(**{**SAFE_PROD, **override})


def test_development_allows_defaults() -> None:
    assert not Settings(ENVIRONMENT="development").is_production


def _request(headers: dict) -> Request:
    raw = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "headers": raw, "client": ("10.0.0.1", 1)})


def test_client_ip_prefers_real_ip_then_forwarded_then_socket() -> None:
    assert client_ip(_request({"X-Real-IP": "41.1.1.1"})) == "41.1.1.1"
    assert client_ip(_request({"X-Forwarded-For": "41.2.2.2, 10.0.0.9"})) == "41.2.2.2"
    assert client_ip(_request({})) == "10.0.0.1"


def test_readyz_checks_database(client) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_bootstrap_creates_active_admin_once(db_session) -> None:
    assert bootstrap_admin(db_session, "Head@School.ng", "a-long-password!") == (
        "created admin head@school.ng"
    )
    admin = db_session.scalar(select(User).where(User.email == "head@school.ng"))
    assert admin.role is UserRole.admin and admin.status is UserStatus.active
    assert "already exists" in bootstrap_admin(db_session, "x@y.ng", "another-long-pass")


@pytest.mark.parametrize("email,password", [("", "a-long-password!"), ("a@b.ng", "short")])
def test_bootstrap_skips_without_safe_credentials(db_session, email, password) -> None:
    assert bootstrap_admin(db_session, email, password).startswith("skipped")
