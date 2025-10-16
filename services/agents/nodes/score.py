"""Scoring node for candidates."""
from __future__ import annotations

import asyncio

from ..providers.base import ScoringProvider
from ..settings import settings
from ..state import GenerationStateDict, ScoredCandidate


def build_score_node(provider: ScoringProvider):
    async def _score(state: GenerationStateDict) -> dict[str, list[ScoredCandidate]]:
        to_score = state.get("filtered") or state.get("candidates") or []
        coro = provider.score(to_score)
        timeout = settings.scoring_time_budget_seconds
        if timeout and timeout > 0:
            scored = await asyncio.wait_for(coro, timeout=timeout)
        else:
            scored = await coro
        progress = dict(state.get("progress", {}))
        progress["scored"] = len(scored)
        return {"scored": list(scored), "filtered": [], "progress": progress}

    return _score
