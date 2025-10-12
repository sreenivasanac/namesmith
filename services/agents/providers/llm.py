"""LLM-backed providers for generation, scoring, and availability."""
from __future__ import annotations

import random
from typing import Any, Iterable, Sequence

from litellm import acompletion

from ..prompts import (
    build_generation_messages,
    build_scoring_messages,
    extract_json_payload,
    parse_generation_payload,
    parse_scoring_payload,
)
from ..settings import settings
from ..state import (
    AvailabilityResult,
    Candidate,
    CompanyExample,
    GenerationInputs,
    ScoredCandidate,
    Trend,
)
from .base import AvailabilityProvider, GenerationProvider, ScoringProvider


def _coerce_candidate(payload: dict[str, str] | Candidate) -> Candidate:
    if isinstance(payload, Candidate):
        return payload
    label = payload.get("label")
    tld = payload.get("tld")
    if not label or not tld:
        raise ValueError("LLM generation payload must include 'label' and 'tld'")
    return Candidate(
        label=label.lower(),
        tld=tld.lower(),
        display_name=payload.get("display_name") or label.capitalize(),
        reasoning=payload.get("reasoning"),
    )


def _coerce_scored_candidate(payload: dict[str, float | str] | ScoredCandidate) -> ScoredCandidate:
    if isinstance(payload, ScoredCandidate):
        return payload
    label = payload.get("label")
    tld = payload.get("tld")
    if not label or not tld:
        raise ValueError("LLM scoring payload must include 'label' and 'tld'")

    def _as_score(value: float | str | None) -> int:
        if value is None:
            return 10
        try:
            return max(1, min(10, int(round(float(value)))))
        except (TypeError, ValueError) as exc:  # noqa: PERF203
            raise ValueError("LLM scoring payload must include numeric scores") from exc

    rationale_raw = payload.get("rationale", "It's a very good domain name.")
    rationale = str(rationale_raw).strip()
    if len(rationale) > 200:
        rationale = rationale[:200]

    return ScoredCandidate(
        label=label.lower(),
        tld=tld.lower(),
        display_name=payload.get("display_name") or label.capitalize(),
        memorability=_as_score(payload.get("memorability")),
        pronounceability=_as_score(payload.get("pronounceability")),
        brandability=_as_score(payload.get("brandability")),
        overall=_as_score(payload.get("overall")),
        rubric_version=str(payload.get("rubric_version", settings.scoring_rubric_version)),
        rationale=rationale,
    )


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
            **self._completion_kwargs,
        )
        content = _extract_message_content(response)
        payload = extract_json_payload(content)
        raw_candidates = parse_generation_payload(payload)
        return [_coerce_candidate(item) for item in raw_candidates]


class LLMScoringProvider(ScoringProvider):
    """Delegate scoring to an injected LLM callable."""

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
            **self._completion_kwargs,
        )
        content = _extract_message_content(response)
        payload = extract_json_payload(content)
        raw_scores = parse_scoring_payload(payload)
        return [_coerce_scored_candidate(item) for item in raw_scores]


class StubAvailabilityProvider(AvailabilityProvider):
    """Return probabilistic availability results to avoid real registrar costs."""

    def __init__(self, registrar: str = "stub") -> None:
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


def build_default_providers(
    *,
    generation_model: str | None = None,
    scoring_model: str | None = None,
) -> tuple[GenerationProvider, ScoringProvider, AvailabilityProvider]:
    from .whoapi import WhoapiAvailabilityProvider
    from .whoisjson import WhoisJsonAvailabilityProvider

    generation = LLMGenerationProvider(model_name=generation_model or settings.generation_model)
    scoring = LLMScoringProvider(model_name=scoring_model or settings.scoring_model)

    provider_name = (settings.registrar_provider or "stub").strip().lower()
    availability: AvailabilityProvider

    if provider_name == "stub":
        availability = StubAvailabilityProvider()
    elif provider_name == "whoapi":
        if not settings.whoapi_api_key:
            availability = StubAvailabilityProvider(registrar="whoapi-missing-key")
        else:
            availability = WhoapiAvailabilityProvider(api_key=settings.whoapi_api_key)
    elif provider_name in {"whoisjson", "whoisjsonapi"}:
        if not settings.whoisjson_api_key:
            availability = StubAvailabilityProvider(registrar="whoisjson-missing-key")
        else:
            availability = WhoisJsonAvailabilityProvider(api_key=settings.whoisjson_api_key)
    else:
        raise ValueError(f"Unsupported registrar provider '{settings.registrar_provider}'")

    return generation, scoring, availability


def _extract_message_content(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not choices:
        raise ValueError("LLM response missing choices")

    first_choice = choices[0]
    
    # Handle Choice objects from litellm/OpenAI SDK
    if hasattr(first_choice, "message"):
        # It's a Choice object, access attributes directly
        message = first_choice.message
        if hasattr(message, "content"):
            content = message.content
        else:
            content = getattr(message, "text", None)
    elif isinstance(first_choice, dict):
        # It's a dict-like response
        message = first_choice.get("message") or {}
        content: Any = message.get("content")
    else:
        # Try to convert to dict if it has __dict__ attribute
        if hasattr(first_choice, "__dict__"):
            first_choice = first_choice.__dict__
            message = first_choice.get("message") or {}
            content = message.get("content")
        else:
            raise ValueError(f"LLM response choice is an unexpected type: {type(first_choice)}")

    if isinstance(content, list):
        text_fragments: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text" and isinstance(item.get("text"), str):
                text_fragments.append(item["text"])
        content = "".join(text_fragments)

    if isinstance(content, str) and content.strip():
        return content

    # Handle delta for streaming responses (if first_choice is dict-like)
    if isinstance(first_choice, dict):
        delta = first_choice.get("delta")
        if isinstance(delta, dict):
            delta_content = delta.get("content")
            if isinstance(delta_content, str) and delta_content.strip():
                return delta_content

        text_field = first_choice.get("text")
        if isinstance(text_field, str) and text_field.strip():
            return text_field
    elif hasattr(first_choice, "delta"):
        # Handle object-based delta
        delta = first_choice.delta
        if hasattr(delta, "content"):
            delta_content = delta.content
            if isinstance(delta_content, str) and delta_content.strip():
                return delta_content
    elif hasattr(first_choice, "text"):
        # Handle object-based text field
        text_field = first_choice.text
        if isinstance(text_field, str) and text_field.strip():
            return text_field

    raise ValueError("LLM response missing message content")


__all__ = [
    "LLMGenerationProvider",
    "LLMScoringProvider",
    "StubAvailabilityProvider",
    "build_default_providers",
]
