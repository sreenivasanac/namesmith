"""Candidate generation node."""
from __future__ import annotations

import asyncio

from ..providers.base import GenerationProvider
from ..settings import settings
from ..state import Candidate, GenerationStateDict


def build_generate_node(provider: GenerationProvider):
    async def _generate(state: GenerationStateDict) -> dict[str, list[Candidate]]:
        coro = provider.generate(
            state["inputs"],
            trends=state.get("trends", []),
            company_examples=state.get("company_examples", []),
        )
        # TODO think if this step needs to be async or sync
        # based on running time
        timeout = settings.generation_time_budget_seconds
        if timeout and timeout > 0:
            candidates = await asyncio.wait_for(coro, timeout=timeout)
        else:
            candidates = await coro
        progress = dict(state.get("progress", {}))
        progress["generated"] = len(candidates)
        return {"candidates": list(candidates), "progress": progress}

    return _generate
