"""Application settings and configuration helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    supabase_jwt_public_key: Optional[str] = Field(default=None, alias="SUPABASE_JWT_PUBLIC_KEY")
    default_tld: list[str] = Field(default_factory=lambda: ["com", "ai"])
    branding_name: str = Field(default="Namesmith")
    agent_model_name: str = Field(default="namesmith-agent")
    registrar_provider: str = Field(default="whoapi")
    registrar_api_key: Optional[str] = Field(default=None, alias="WHOAPI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
