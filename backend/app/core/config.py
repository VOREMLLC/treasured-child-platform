"""Application configuration.

Loads settings from environment variables (with .env file support in
dev). Values are validated once at startup; access them via
``from app.core.config import settings``.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration in one place.

    The keys below mirror the ones in the root ``.env.example``. Keys
    used by features not yet built (JWT, Paystack, Anthropic) are still
    declared so ``.env`` is validated up-front rather than at the first
    request to that feature.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # ---- Database ----
    DATABASE_URL: str = Field(
        default="sqlite:///./local.db",
        description=(
            "SQLAlchemy database URL. Defaults to local SQLite. "
            "Production sets this to a Postgres URL "
            "(e.g. postgresql+psycopg://user:pass@host:5432/treasured_child)."
        ),
    )

    # ---- Auth (used by S7+; declared early so .env is validated) ----
    JWT_SECRET: str = Field(default="change-me-in-production")
    JWT_ACCESS_TTL_MIN: int = Field(default=15)
    JWT_REFRESH_TTL_DAYS: int = Field(default=30)


settings = Settings()
