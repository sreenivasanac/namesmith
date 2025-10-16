import pytest

from packages.shared_py.namesmith_schemas.registrars import DomainAvailabilityProvider
from services.agents.providers import llm
from services.agents.providers.llm import build_default_providers
from services.agents.providers.whoisjson import WhoisJsonAvailabilityProvider


class DummyAgentSettings:
    def __init__(
        self,
        *,
        registrar_provider: DomainAvailabilityProvider | str,
        whoapi_key: str | None = None,
        whoisjson_key: str | None = None,
    ) -> None:
        self.generation_model = "dummy-generation"
        self.scoring_model = "dummy-scoring"
        self.registrar_provider = registrar_provider
        self.whoapi_key = whoapi_key
        self.whoisjsonapi_key = whoisjson_key
        self.dns_timeout_seconds = 5.0

    def get_domain_availability_api_key(
        self, provider: DomainAvailabilityProvider | str
    ) -> str | None:
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


def test_build_default_providers_requires_api_key():
    original_settings = llm.settings
    dummy = DummyAgentSettings(registrar_provider=DomainAvailabilityProvider.WHOAPI)
    try:
        llm.settings = dummy

        with pytest.raises(ValueError, match="WhoAPI API key must be configured"):
            build_default_providers()
    finally:
        llm.settings = original_settings


def test_build_default_providers_uses_dict_api_key():
    original_settings = llm.settings
    dummy = DummyAgentSettings(
        registrar_provider=DomainAvailabilityProvider.WHOISJSONAPI,
        whoisjson_key="token-123",
    )
    try:
        llm.settings = dummy

        _, _, availability = build_default_providers()

        assert isinstance(availability, WhoisJsonAvailabilityProvider)
        assert availability._api_key == "token-123"
    finally:
        llm.settings = original_settings
