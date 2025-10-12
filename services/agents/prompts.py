"""Prompt assembly and parsing helpers for LiteLLM-backed providers."""
from __future__ import annotations

import json
from textwrap import dedent
from typing import Any, Sequence

from .state import Candidate, CompanyExample, GenerationInputs, Trend

# TODO update the logic with old_code and our own logic to make this better
def build_generation_messages(
    inputs: GenerationInputs,
    trends: Sequence[Trend],
    company_examples: Sequence[CompanyExample],
) -> list[dict[str, str]]:
    trend_lines = [f"- {trend.title}" + (f": {trend.summary}" if trend.summary else "") for trend in trends]
    example_lines = [
        f"- {example.name}" + (f" ({example.domain})" if example.domain else "") + (f": {example.description}" if example.description else "")
        for example in company_examples
    ]

    user_context_chunks: list[str] = []
    if inputs.topic:
        user_context_chunks.append(f"Topic focus: {inputs.topic}")
    if inputs.prompt:
        user_context_chunks.append(f"Business prompt: {inputs.prompt}")
    if inputs.categories:
        user_context_chunks.append("Target categories: " + ", ".join(inputs.categories))
    if inputs.tlds:
        user_context_chunks.append("Preferred TLDs: " + ", ".join(inputs.tlds))

    system_instructions = dedent(
        """
        You are an expert brand strategist who crafts inventive, pronounceable domain names.
        Generate concise, original domain labels without numbers or hyphens unless explicitly requested.
        Each idea must include:
        - label: lowercase domain label
        - tld: TLD (default to popular choices if unspecified)
        - display_name: human-friendly capitalization of the label
        - reasoning: short phrase (<20 words) explaining the name
        Reply with a pure JSON array containing between 10 and 25 objects. No prose, no code fences.
        """
    ).strip()

    user_parts = []
    if user_context_chunks:
        user_parts.append("\n".join(user_context_chunks))
    if trend_lines:
        user_parts.append("Relevant trends:\n" + "\n".join(trend_lines))
    if example_lines:
        user_parts.append("Reference companies:\n" + "\n".join(example_lines))

    user_prompt = "\n\n".join(user_parts) if user_parts else "Create distinct, premium-sounding domain names."

    return [
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": user_prompt},
    ]


def build_scoring_messages(candidates: Sequence[Candidate]) -> list[dict[str, str]]:
    candidate_payload = [
        {
            "label": candidate.label,
            "tld": candidate.tld,
            "display_name": candidate.display_name,
        }
        for candidate in candidates
    ]

    system_instructions = dedent(
        """
        You are evaluating candidate brand names. Score each according to the rubric below.
        Return a JSON array where every object includes:
        - label (lowercase)
        - tld
        - display_name (optional)
        - memorability (integer 1-10)
        - pronounceability (integer 1-10)
        - brandability (integer 1-10)
        - overall (integer 1-10)
        - rationale (max 25 words)
        Output JSON only, use integer scores, no commentary or code fences.
        """
    ).strip()

    user_prompt = "Candidates to score:\n" + json.dumps(candidate_payload, ensure_ascii=False)

    return [
        {"role": "system", "content": system_instructions},
        {"role": "user", "content": user_prompt},
    ]


def extract_json_payload(content: str) -> Any:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2:
            text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:  # noqa: PERF203
        raise ValueError("LLM response was not valid JSON") from exc


def parse_generation_payload(payload: Any) -> Sequence[dict[str, str]]:
    if not isinstance(payload, list):
        raise ValueError("Generation response must be a JSON array")
    results: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Each generation item must be an object")
        results.append(item)
    return results


def parse_scoring_payload(payload: Any) -> Sequence[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValueError("Scoring response must be a JSON array")
    results: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Each scoring item must be an object")
        results.append(item)
    return results


__all__ = [
    "build_generation_messages",
    "build_scoring_messages",
    "extract_json_payload",
    "parse_generation_payload",
    "parse_scoring_payload",
]
