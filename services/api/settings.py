"""Application settings and configuration helpers."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    database_url: str = Field(alias="DATABASE_URL")
    default_tld: list[str] = Field(default_factory=lambda: ["com", "ai"])
    branding_name: str = Field(default="Namesmith")
    agent_model_name: str = Field(default="namesmith-agent")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
