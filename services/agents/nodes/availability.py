"""Availability nodes."""
from __future__ import annotations

import asyncio

from ..providers.base import AvailabilityProvider
from ..settings import settings
from ..state import AvailabilityResult, GenerationStateDict


def build_availability_node(provider: AvailabilityProvider):
    async def _availability(state: GenerationStateDict) -> dict[str, list[AvailabilityResult]]:
        candidates = state.get("scored") or state.get("filtered") or state.get("candidates") or []
        coro = provider.check(candidates)
        timeout = settings.availability_time_budget_seconds
        if timeout and timeout > 0:
            results = await asyncio.wait_for(coro, timeout=timeout)
        else:
            results = await coro
        progress = dict(state.get("progress", {}))
        progress["availability_checked"] = len(results)
        return {
            "availability": list(results),
            "candidates": [],
            "filtered": [],
            "progress": progress,
        }

    return _availability
