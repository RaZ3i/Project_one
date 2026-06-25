import os
from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import make_url

_LOCALHOST_DEFAULT = "postgresql+asyncpg://tutoring:tutoring@localhost:5432/tutoring"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = _LOCALHOST_DEFAULT
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8000"
    ALGORITHM: str = "HS256"

    @field_validator("DATABASE_URL")
    @classmethod
    def database_url_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(
                "DATABASE_URL is empty. Set it on the Railway WEB service (not only on "
                "Postgres) using a variable reference, e.g. ${{Postgres.DATABASE_URL}}."
            )
        return value.strip()

    @model_validator(mode="after")
    def reject_localhost_on_railway(self) -> "Settings":
        on_railway = bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"))
        if on_railway and self.DATABASE_URL == _LOCALHOST_DEFAULT:
            raise ValueError(
                "DATABASE_URL is not set on this Railway service (still using localhost). "
                "Open the WEB service → Variables → add DATABASE_URL as a Reference to "
                "Postgres, e.g. ${{Postgres.DATABASE_URL}}, then redeploy."
            )
        return self

    def _parsed_database_url(self):
        try:
            return make_url(self.DATABASE_URL)
        except Exception as exc:
            raise ValueError(
                f"DATABASE_URL is not a valid SQLAlchemy URL: {exc}. "
                "If the password contains special characters, URL-encode them."
            ) from exc

    @property
    def async_database_url(self) -> str:
        parsed = self._parsed_database_url()
        driver = parsed.drivername
        if driver in ("postgresql", "postgres"):
            return str(parsed.set(drivername="postgresql+asyncpg"))
        if driver == "postgresql+asyncpg":
            return str(parsed)
        return self.DATABASE_URL

    @property
    def sync_database_url(self) -> str:
        """Sync driver URL for Alembic migrations (psycopg2)."""
        parsed = self._parsed_database_url()
        driver = parsed.drivername
        if driver in ("postgresql", "postgres", "postgresql+asyncpg"):
            return str(parsed.set(drivername="postgresql+psycopg2"))
        if driver == "postgresql+psycopg2":
            return str(parsed)
        return self.DATABASE_URL

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
