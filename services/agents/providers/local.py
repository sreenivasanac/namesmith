"""LLM-first providers for generation, scoring, and availability."""
from __future__ import annotations

from typing import Awaitable, Callable, Iterable, Sequence

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

GenerationLLMFn = Callable[
    [GenerationInputs, Sequence[Trend], Sequence[CompanyExample]],
    Awaitable[Sequence[dict[str, str] | Candidate]],
]

ScoringLLMFn = Callable[
    [Sequence[Candidate]],
    Awaitable[Sequence[dict[str, float | str] | ScoredCandidate]],
]


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
    return ScoredCandidate(
        label=label.lower(),
        tld=tld.lower(),
        display_name=payload.get("display_name") or label.capitalize(),
        memorability=float(payload.get("memorability", 0)),
        pronounceability=float(payload.get("pronounceability", 0)),
        brandability=float(payload.get("brandability", 0)),
        overall=float(payload.get("overall", 0)),
        rubric_version=str(payload.get("rubric_version", settings.scoring_rubric_version)),
        rationale=str(payload.get("rationale", "")) or None,
    )


class LLMGenerationProvider(GenerationProvider):
    """Delegate generation to an injected LLM callable."""

    def __init__(self, llm_fn: GenerationLLMFn | None = None) -> None:
        self._llm_fn = llm_fn

    async def generate(
        self,
        inputs: GenerationInputs,
        *,
        trends: Sequence[Trend],
        company_examples: Sequence[CompanyExample],
    ) -> Sequence[Candidate]:
        if self._llm_fn is None:
            raise RuntimeError("LLM generation callable is not configured")
        raw_candidates = await self._llm_fn(inputs, trends, company_examples)
        return [_coerce_candidate(item) for item in raw_candidates]


class LLMScoringProvider(ScoringProvider):
    """Delegate scoring to an injected LLM callable."""

    def __init__(self, llm_fn: ScoringLLMFn | None = None) -> None:
        self._llm_fn = llm_fn

    async def score(self, candidates: Sequence[Candidate]) -> Sequence[ScoredCandidate]:
        if self._llm_fn is None:
            raise RuntimeError("LLM scoring callable is not configured")
        raw_scores = await self._llm_fn(candidates)
        return [_coerce_scored_candidate(item) for item in raw_scores]


class StubAvailabilityProvider(AvailabilityProvider):
    """Return unknown availability to defer registrar costs during development."""

    def __init__(self, registrar: str = "stub") -> None:
        self._registrar = registrar

    async def check(self, candidates: Iterable[Candidate | ScoredCandidate]) -> Sequence[AvailabilityResult]:
        results: list[AvailabilityResult] = []
        for candidate in candidates:
            results.append(
                AvailabilityResult(
                    full_domain=candidate.full_domain,
                    status="unknown",
                    registrar=self._registrar,
                )
            )
        return results


def build_default_providers() -> tuple[GenerationProvider, ScoringProvider, AvailabilityProvider]:
    generation = LLMGenerationProvider()
    scoring = LLMScoringProvider()
    availability: AvailabilityProvider
    if settings.registrar_provider.lower() == "stub" or not settings.whoapi_api_key:
        availability = StubAvailabilityProvider(registrar=settings.registrar_provider)
    else:
        from .whoapi import WhoapiAvailabilityProvider

        availability = WhoapiAvailabilityProvider(api_key=settings.whoapi_api_key)

    return generation, scoring, availability
