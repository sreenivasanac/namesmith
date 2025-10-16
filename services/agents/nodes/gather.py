"""Context gathering nodes for agent workflow."""
from __future__ import annotations

from ..state import GenerationStateDict


async def gather_context(state: GenerationStateDict) -> dict[str, list]:
    return {
        "trends": [],
        "company_examples": [],
    }
