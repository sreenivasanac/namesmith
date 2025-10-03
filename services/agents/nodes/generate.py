"""Candidate generation node."""
from __future__ import annotations

from ..providers.base import GenerationProvider
from ..state import Candidate, GenerationStateDict


def build_generate_node(provider: GenerationProvider):
    async def _generate(state: GenerationStateDict) -> dict[str, list[Candidate]]:
        candidates = await provider.generate(
            state["inputs"],
            trends=state.get("trends", []),
            company_examples=state.get("company_examples", []),
        )
        progress = dict(state.get("progress", {}))
        progress["generated"] = len(candidates)
        return {"candidates": list(candidates), "progress": progress}

    return _generate
