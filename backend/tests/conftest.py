"""Pytest fixtures.

- ``disable_rate_limit`` (autouse) keeps slowapi from tripping during
  test runs.
- ``clear_email_outbox`` (autouse) gives every test a clean in-memory
  email buffer.
- ``db_session`` builds a fresh in-memory SQLite database with the full
  schema for one test.
- ``client`` returns a FastAPI ``TestClient`` whose ``get_db``
  dependency yields the ``db_session`` fixture, so the endpoint and the
  test share one session — anything the endpoint commits is visible to
  the test.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  # registers all models on Base
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.services import email as email_service


@pytest.fixture(autouse=True)
def disable_rate_limit():
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture(autouse=True)
def clear_email_outbox():
    email_service.clear_outbox()
    yield
    email_service.clear_outbox()


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
