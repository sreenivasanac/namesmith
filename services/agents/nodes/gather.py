"""Context gathering nodes for agent workflow."""
from __future__ import annotations

from ..state import CompanyExample, GenerationStateDict, Trend


async def gather_context(state: GenerationStateDict) -> dict[str, list]:
    # TODO(agents-context): replace placeholder token heuristics with real data sources for
    # business and investor flows once datasets are wired up. See project docs for details.
    inputs = state["inputs"]
    topic_tokens = _tokenize(inputs.topic)
    prompt_tokens = _tokenize(inputs.prompt)

    trends = [
        Trend(title=token.capitalize(), summary=f"Emerging interest around {token}")
        for token in topic_tokens[:5]
    ]

    company_examples = [
        CompanyExample(
            name=f"{token.title()} Labs",
            domain=f"{token.lower()}labs.com",
            description=f"Example company operating in {token} space.",
            categories=[token],
            source="heuristic",
        )
        for token in (topic_tokens + prompt_tokens)[:5]
    ]

    return {
        "trends": trends,
        "company_examples": company_examples,
    }


def _tokenize(text: str | None) -> list[str]:
    if not text:
        return []
    cleaned = text.replace("/", " ").replace("-", " ")
    tokens = [token.strip().lower() for token in cleaned.split() if len(token.strip()) >= 3]
    unique_tokens: list[str] = []
    for token in tokens:
        if token not in unique_tokens:
            unique_tokens.append(token)
    return unique_tokens
