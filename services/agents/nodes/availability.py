"""Availability nodes."""
from __future__ import annotations

from ..providers.base import AvailabilityProvider
from ..state import AvailabilityResult, GenerationStateDict


def build_availability_node(provider: AvailabilityProvider):
    async def _availability(state: GenerationStateDict) -> dict[str, list[AvailabilityResult]]:
        candidates = state.get("scored") or state.get("filtered") or state.get("candidates") or []
        results = await provider.check(candidates)
        progress = dict(state.get("progress", {}))
        progress["availability_checked"] = len(results)
        return {
            "availability": list(results),
            "candidates": [],
            "filtered": [],
            "progress": progress,
        }

    return _availability
