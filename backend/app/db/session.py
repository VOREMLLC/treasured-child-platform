"""SQLAlchemy engine and session management.

One engine per process; SessionLocal is a factory that hands out
short-lived Session objects. FastAPI routes get a session via the
``get_db`` dependency.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# SQLite needs `check_same_thread=False` to use the engine across
# threads (FastAPI handles requests in a thread pool). Other dialects
# do not need this kwarg.
connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy ``Session``.

    Use with ``Depends(get_db)`` on any route that needs DB access.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
