"""Alembic migration environment.

Reads DATABASE_URL from the application settings (.env via
app.core.config) so migrations always target the same database the app
talks to. Also imports every model module so Alembic's autogenerate can
see the full schema via Base.metadata.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# These imports register every model with Base.metadata.
from app.core.config import settings
from app.models.base import Base
import app.models  # noqa: F401  # registers all models on Base

# Alembic Config object — gives access to the values in alembic.ini.
config = context.config

# Override the URL in alembic.ini with the one loaded from .env.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate SQL without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations against a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
