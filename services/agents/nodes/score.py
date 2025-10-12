"""Scoring node for candidates."""
from __future__ import annotations

from ..providers.base import ScoringProvider
from ..state import GenerationStateDict, ScoredCandidate


def build_score_node(provider: ScoringProvider):
    async def _score(state: GenerationStateDict) -> dict[str, list[ScoredCandidate]]:
        to_score = state.get("filtered") or state.get("candidates") or []
        scored = await provider.score(to_score)
        progress = dict(state.get("progress", {}))
        progress["scored"] = len(scored)
        return {"scored": list(scored), "filtered": [], "progress": progress}

    return _score
