"""Tests for Settings normalisation of hosted-Postgres URLs."""

from __future__ import annotations

import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    "raw",
    [
        "postgres://u:p@host:5432/db",
        "postgresql://u:p@host:5432/db",
        "postgresql+psycopg://u:p@host:5432/db",
    ],
)
def test_postgres_urls_use_psycopg3(raw: str) -> None:
    settings = Settings(DATABASE_URL=raw)
    assert settings.DATABASE_URL == "postgresql+psycopg://u:p@host:5432/db"


def test_sqlite_url_is_untouched() -> None:
    settings = Settings(DATABASE_URL="sqlite:///./local.db")
    assert settings.DATABASE_URL == "sqlite:///./local.db"
