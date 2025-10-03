"""Filtering and deduplication node."""
from __future__ import annotations

from ..state import Candidate, GenerationStateDict

_ALLOWED_LENGTH_RANGE = (4, 12)


def dedupe_and_filter(state: GenerationStateDict) -> dict[str, list[Candidate]]:
    inputs = state["inputs"]
    seen: set[str] = set()
    filtered: list[Candidate] = []
    for candidate in state.get("candidates", []):
        label = candidate.label.lower()
        if label in seen:
            continue
        if not _ALLOWED_LENGTH_RANGE[0] <= len(label) <= _ALLOWED_LENGTH_RANGE[1]:
            continue
        seen.add(label)
        filtered.append(candidate)
        if len(filtered) >= inputs.count:
            break
    progress = dict(state.get("progress", {}))
    progress["filtered"] = len(filtered)
    return {"filtered": filtered, "candidates": [], "progress": progress}
