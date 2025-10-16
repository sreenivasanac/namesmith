"""Agent service configuration."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from packages.shared_py.namesmith_schemas.registrars import DomainAvailabilityProvider


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("services/agents/.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    database_url: str = Field(alias="DATABASE_URL")
    branding_name: str = Field(default="Namesmith")
    generation_model: str = Field(default="gpt-4o-mini")
    scoring_model: str = Field(default="gpt-4o-mini")
    model_allowlist: list[str] = Field(default_factory=list)
    scoring_rubric_version: str = Field(default="v1")
    registrar_provider: DomainAvailabilityProvider = Field(
        default=DomainAvailabilityProvider.WHOISJSONAPI,
        alias="REGISTRAR_PROVIDER",
    )
    whoapi_key: Optional[str] = Field(default=None, alias="WHOAPI_KEY")
    whoisjsonapi_key: Optional[str] = Field(default=None, alias="WHOISJSON_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    generation_concurrency_limit: int = Field(default=8, alias="GENERATION_CONCURRENCY_LIMIT")
    availability_concurrency_limit: int = Field(default=5, alias="AVAILABILITY_CONCURRENCY_LIMIT")
    generation_time_budget_seconds: float = Field(default=60.0, alias="GENERATION_TIME_BUDGET_SECONDS")
    scoring_time_budget_seconds: float = Field(default=60.0, alias="SCORING_TIME_BUDGET_SECONDS")
    availability_time_budget_seconds: float = Field(default=90.0, alias="AVAILABILITY_TIME_BUDGET_SECONDS")
    availability_success_threshold: float = Field(default=0.8, alias="AVAILABILITY_SUCCESS_THRESHOLD")
    dns_timeout_seconds: float = Field(default=5.0, alias="DNS_TIMEOUT_SECONDS")
    scoring_rubric_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "memorability": 7,
            "pronounceability": 8,
            "brandability": 6,
            "overall": 8,
        },
        alias="SCORING_RUBRIC_WEIGHTS",
    )

    def get_domain_availability_api_key(
        self, provider: DomainAvailabilityProvider | str
    ) -> Optional[str]:
        provider_enum = (
            provider
            if isinstance(provider, DomainAvailabilityProvider)
            else DomainAvailabilityProvider.from_str(provider)
        )
        if provider_enum is DomainAvailabilityProvider.WHOAPI:
            return self.whoapi_key
        if provider_enum is DomainAvailabilityProvider.WHOISJSONAPI:
            return self.whoisjsonapi_key
        return None

    @property
    def whoapi_api_key(self) -> Optional[str]:
        return self.whoapi_key

    @property
    def whoisjson_api_key(self) -> Optional[str]:
        return self.whoisjsonapi_key


@lru_cache
def get_settings() -> AgentSettings:
    return AgentSettings()


settings = get_settings()
