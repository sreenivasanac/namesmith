"""Application settings and configuration helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from packages.shared_py.namesmith_schemas.registrars import DomainAvailabilityProvider


DEFAULT_ASYNC_PG_STATEMENT_CACHE_SIZE = 0


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    database_url: str = Field(alias="DATABASE_URL")
    supabase_jwt_public_key: Optional[str] = Field(default=None, alias="SUPABASE_JWT_PUBLIC_KEY")
    default_tld: list[str] = Field(default_factory=lambda: ["com", "ai"])
    branding_name: str = Field(default="Namesmith")
    agent_model_name: str = Field(default="namesmith-agent")
    asyncpg_statement_cache_size: int = Field(
        default=DEFAULT_ASYNC_PG_STATEMENT_CACHE_SIZE, alias="ASYNC_PG_STATEMENT_CACHE_SIZE"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
