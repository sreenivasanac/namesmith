"""LLM-backed providers for generation, scoring, and availability."""
from __future__ import annotations

import json
import logging
import random
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Sequence

from litellm import acompletion
from pydantic import BaseModel, TypeAdapter

from ..prompts import (
    build_generation_messages,
    build_scoring_messages,
    extract_json_payload,
    parse_generation_payload,
    parse_scoring_payload,
)
from ..settings import settings
from packages.shared_py.namesmith_schemas.registrars import DomainAvailabilityProvider

from ..state import (
    AvailabilityResult,
    Candidate,
    CompanyExample,
    GenerationInputs,
    ScoredCandidate,
    Trend,
)
from .base import AvailabilityProvider, GenerationProvider, ScoringProvider


class CandidateList(BaseModel):
    items: list[Candidate]


class ScoredCandidateList(BaseModel):
    items: list[ScoredCandidate]


class LLMGenerationProvider(GenerationProvider):
    """Delegate generation to an injected LLM callable."""

    def __init__(
        self,
        *,
        model_name: str,
        temperature: float = 0.7,
        completion_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._model_name = model_name
        self._temperature = temperature
        self._completion_kwargs = completion_kwargs or {}

    async def generate(
        self,
        inputs: GenerationInputs,
        *,
        trends: Sequence[Trend],
        company_examples: Sequence[CompanyExample],
    ) -> Sequence[Candidate]:
        messages = build_generation_messages(inputs, trends, company_examples)
        response = await acompletion(
            model=self._model_name,
            messages=messages,
            temperature=self._temperature,
            # Hint to supported providers to produce a JSON object with 'items'
            response_format=CandidateList,
            **self._completion_kwargs,
        )
        logger.info("LLM response (generation): %s", _format_llm_response(response))
        content = _extract_message_content(response)
        payload = extract_json_payload(content)
        # Accept either {items: [...]} or raw list for backward compatibility
        if isinstance(payload, dict) and "items" in payload:
            try:
                parsed = CandidateList.model_validate(payload)
                return list(TypeAdapter(list[Candidate]).validate_python(parsed.items))
            except Exception:
                pass
        raw_candidates = parse_generation_payload(payload)
        return list(TypeAdapter(list[Candidate]).validate_python(raw_candidates))


class LLMScoringProvider(ScoringProvider):

    def __init__(
        self,
        *,
        model_name: str,
        temperature: float = 0.4,
        completion_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._model_name = model_name
        self._temperature = temperature
        self._completion_kwargs = completion_kwargs or {}

    async def score(self, candidates: Sequence[Candidate]) -> Sequence[ScoredCandidate]:
        if not candidates:
            return []
        messages = build_scoring_messages(candidates)
        response = await acompletion(
            model=self._model_name,
            messages=messages,
            temperature=self._temperature,
            response_format=ScoredCandidateList,
            **self._completion_kwargs,
        )
        logger.info("LLM response (scoring): %s", _format_llm_response(response))
        content = _extract_message_content(response)
        payload = extract_json_payload(content)
        raw_scores = parse_scoring_payload(payload)
        adjusted: list[dict[str, Any]] = []
        weights = settings.scoring_rubric_weights or {}
        total_weight = sum(weights.values())
        for item in raw_scores:
            if item.get("overall") is None:
                m = item.get("memorability")
                p = item.get("pronounceability")
                b = item.get("brandability")
                try:
                    m_f, p_f, b_f = int(m), int(p), int(b)
                except Exception:
                    m_f, p_f, b_f = 10, 10, 10
                item["overall"] = int((m_f + p_f + b_f) / 3)
            adjusted.append(item)
        # Try strict schema first if provider returned object
        if isinstance(payload, dict) and "items" in payload:
            try:
                parsed = ScoredCandidateList.model_validate({"items": adjusted})
                return list(TypeAdapter(list[ScoredCandidate]).validate_python(parsed.items))
            except Exception:
                pass
        return list(TypeAdapter(list[ScoredCandidate]).validate_python(adjusted))


class StubAvailabilityProvider(AvailabilityProvider):
    """Return probabilistic availability results to avoid real registrar costs."""

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float | None = None,
        registrar: str = "stub",
    ) -> None:
        self._api_key = api_key  # Unused but kept for consistency
        self._timeout = timeout  # Unused but kept for consistency
        self._registrar = registrar

    async def check(self, candidates: Iterable[Candidate | ScoredCandidate]) -> Sequence[AvailabilityResult]:
        results: list[AvailabilityResult] = []
        for candidate in candidates:
            is_available = random.random() < 0.8
            results.append(
                AvailabilityResult(
                    full_domain=candidate.full_domain,
                    status="available" if is_available else "registered",
                    registrar=self._registrar,
                    raw_payload={"source": "stub", "probability_available": 0.8},
                )
            )
        return results


@dataclass(frozen=True)
class AvailabilityProviderRegistration:
    requires_api_key: bool
    factory: Callable[[str], AvailabilityProvider]
    missing_key_error: str | None = None


def _create_availability_provider_registry() -> dict[DomainAvailabilityProvider, AvailabilityProviderRegistration]:
    from .whoapi import WhoapiAvailabilityProvider
    from .whoisjson import WhoisJsonAvailabilityProvider

    # TODO reduce this code to be more modular / Code design.
    timeout = settings.dns_timeout_seconds

    return {
        DomainAvailabilityProvider.STUB: AvailabilityProviderRegistration(
            requires_api_key=False,
            factory=lambda api_key: StubAvailabilityProvider(api_key=api_key, timeout=timeout),
        ),
        DomainAvailabilityProvider.WHOAPI: AvailabilityProviderRegistration(
            requires_api_key=True,
            factory=lambda api_key: WhoapiAvailabilityProvider(api_key=api_key, timeout=timeout),
            missing_key_error="WhoAPI API key must be configured to use 'whoapi' registrar provider.",
        ),
        DomainAvailabilityProvider.WHOISJSONAPI: AvailabilityProviderRegistration(
            requires_api_key=True,
            factory=lambda api_key: WhoisJsonAvailabilityProvider(api_key=api_key, timeout=timeout),
            missing_key_error="WhoisJSON API key must be configured to use 'whoisjson' registrar provider.",
        ),
    }


_AVAILABILITY_PROVIDER_REGISTRY = _create_availability_provider_registry()


def build_default_providers(
    *,
    generation_model: str | None = None,
    scoring_model: str | None = None,
) -> tuple[GenerationProvider, ScoringProvider, AvailabilityProvider]:
    generation = LLMGenerationProvider(model_name=generation_model or settings.generation_model)
    scoring = LLMScoringProvider(model_name=scoring_model or settings.scoring_model)

    provider_setting = settings.registrar_provider
    if provider_setting is None:
        raise ValueError("Registrar provider must be configured; stub provider is reserved for tests.")

    if isinstance(provider_setting, str):
        normalized = provider_setting.strip()
        if not normalized:
            raise ValueError("Registrar provider must be configured; stub provider is reserved for tests.")
        try:
            provider_setting = DomainAvailabilityProvider.from_str(normalized)
        except ValueError as exc:
            raise ValueError(f"Unsupported registrar provider '{provider_setting}'") from exc

    registration = _AVAILABILITY_PROVIDER_REGISTRY.get(provider_setting)
    if registration is None:
        raise ValueError(f"Unsupported registrar provider '{provider_setting}'")

    api_key = settings.get_domain_availability_api_key(provider_setting)
    if registration.requires_api_key and not api_key:
        message = registration.missing_key_error or (
            f"API key must be configured to use '{provider_setting.value}' registrar provider."
        )
        raise ValueError(message)

    availability = registration.factory(api_key or "mock-api-key")

    return generation, scoring, availability


def _extract_message_content(response: Any) -> str:
    """Extract text content from LiteLLM responses.

    LiteLLM returns OpenAI-compatible dict with structure:
    - dict["choices"][0]["message"]["content"] (chat completion)
    """
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, TypeError, IndexError) as e:
        raise ValueError(f"Failed to extract content from LLM response: {e}") from e


def _format_llm_response(response: Any) -> str:
    if hasattr(response, "model_dump_json"):
        try:
            return response.model_dump_json()
        except Exception:
            pass
    if hasattr(response, "model_dump"):
        try:
            return json.dumps(response.model_dump(), ensure_ascii=False)
        except Exception:
            pass
    try:
        return json.dumps(response, ensure_ascii=False)
    except TypeError:
        return repr(response)


logger = logging.getLogger(__name__)


__all__ = [
    "LLMGenerationProvider",
    "LLMScoringProvider",
    "StubAvailabilityProvider",
    "build_default_providers",
]
