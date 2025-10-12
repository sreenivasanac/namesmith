"""Agent service configuration."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("services/agents/.env", ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = Field(alias="DATABASE_URL")
    branding_name: str = Field(default="Namesmith")
    generation_model: str = Field(default="gpt-4o-mini")
    scoring_model: str = Field(default="gpt-4o-mini")
    model_allowlist: list[str] = Field(default_factory=list)
    scoring_rubric_version: str = Field(default="v1")
    registrar_provider: str = Field(default="whoisjson")
    whoapi_api_key: Optional[str] = Field(default=None, alias="WHOAPI_API_KEY")
    whoisjson_api_key: Optional[str] = Field(default=None, alias="WHOISJSON_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")


@lru_cache
def get_settings() -> AgentSettings:
    return AgentSettings()


settings = get_settings()
