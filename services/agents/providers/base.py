"""Provider interfaces for agents."""
from __future__ import annotations

import abc
from typing import Iterable, Sequence

from ..state import AvailabilityResult, Candidate, CompanyExample, ScoredCandidate, Trend
from ..state import GenerationInputs


class GenerationProvider(abc.ABC):
    @abc.abstractmethod
    async def generate(
        self,
        inputs: GenerationInputs,
        *,
        trends: Sequence[Trend],
        company_examples: Sequence[CompanyExample],
    ) -> Sequence[Candidate]:
        """Generate domain name candidates."""


class ScoringProvider(abc.ABC):
    @abc.abstractmethod
    async def score(self, candidates: Sequence[Candidate]) -> Sequence[ScoredCandidate]:
        """Score generated domain names."""


class AvailabilityProvider(abc.ABC):
    @abc.abstractmethod
    async def check(self, candidates: Iterable[Candidate | ScoredCandidate]) -> Sequence[AvailabilityResult]:
        """Check registrar availability for a set of domains."""


__all__ = ["GenerationProvider", "ScoringProvider", "AvailabilityProvider"]
