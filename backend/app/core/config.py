"""Application configuration.

Loads settings from environment variables (with .env file support in
dev). Values are validated once at startup; access them via
``from app.core.config import settings``.
"""

from __future__ import annotations

from typing import List

from pydantic import Field, field_validator, model_validator
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

    # ---- Environment ----
    ENVIRONMENT: str = Field(
        default="development",
        description=(
            "'production' turns on Secure cookies and refuses to boot with "
            "placeholder secrets or SQLite."
        ),
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

    # ---- CORS ----
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description=(
            "Allowed Origins for browser CORS. Frontend dev server runs "
            "on http://localhost:3000."
        ),
    )

    # ---- Email ----
    ADMIN_EMAIL: str = Field(
        default="admissions@treasuredchild.example",
        description="Inbox that receives admission application notifications.",
    )

    # ---- Auth (used by S7+; declared early so .env is validated) ----
    JWT_SECRET: str = Field(default="change-me-in-production")
    JWT_ACCESS_TTL_MIN: int = Field(default=15)
    JWT_REFRESH_TTL_DAYS: int = Field(default=30)

    # ---- Password reset (S9) ----
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description=(
            "Public-facing URL of the frontend. Used in password-reset "
            "emails to construct the reset link."
        ),
    )
    RESET_TOKEN_TTL_MIN: int = Field(
        default=60,
        description="Lifetime of a password-reset token in minutes.",
    )

    # ---- Paystack (S11) ----
    PAYSTACK_SECRET_KEY: str = Field(default="sk_test_xxx")
    PAYSTACK_PUBLIC_KEY: str = Field(default="pk_test_xxx")
    PAYSTACK_API_URL: str = Field(
        default="https://api.paystack.co",
        description="Paystack API base URL. Don't include a trailing slash.",
    )

    # ---- AI agent runtime (S23) ----
    ANTHROPIC_API_KEY: str = Field(
        default="sk-ant-xxx",
        description="Anthropic API key. Get one at console.anthropic.com.",
    )
    AGENT_MODEL: str = Field(
        default="claude-sonnet-4-6",
        description="Anthropic model ID used by the VOREM tutor agent.",
    )
    AGENT_MAX_TOKENS: int = Field(
        default=1024,
        description="Max tokens the tutor may generate per call.",
    )

    # ---- First admin (created by scripts.bootstrap_admin on deploy) ----
    BOOTSTRAP_ADMIN_EMAIL: str = Field(default="")
    BOOTSTRAP_ADMIN_PASSWORD: str = Field(default="")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @model_validator(mode="after")
    def _refuse_unsafe_production_config(self) -> "Settings":
        """Fail at boot rather than run production with forgeable secrets.

        A default JWT secret lets anyone mint an admin token; a default
        Paystack key lets anyone sign a fake ``charge.success`` webhook.
        """
        if not self.is_production:
            return self
        problems: List[str] = []
        if self.DATABASE_URL.startswith("sqlite"):
            problems.append("DATABASE_URL must point at Postgres, not SQLite")
        if self.JWT_SECRET == "change-me-in-production" or len(self.JWT_SECRET) < 32:
            problems.append("JWT_SECRET must be a random string of 32+ characters")
        if self.PAYSTACK_SECRET_KEY in ("", "sk_test_xxx"):
            problems.append("PAYSTACK_SECRET_KEY is unset")
        if problems:
            raise ValueError("Unsafe production config: " + "; ".join(problems))
        return self

    @field_validator("DATABASE_URL")
    @classmethod
    def _use_psycopg3_driver(cls, value: str) -> str:
        """Point bare Postgres URLs at the psycopg (v3) driver.

        Hosts such as Railway and Heroku hand out ``postgres://`` or
        ``postgresql://`` URLs. SQLAlchemy maps those to psycopg2, which
        is not installed, so the app would crash at boot.
        """
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value[len(prefix):]
        return value


settings = Settings()
