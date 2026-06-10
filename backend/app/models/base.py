"""SQLAlchemy declarative base.

Every ORM model in :mod:`app.models` inherits from ``Base``.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common base for all ORM models."""
