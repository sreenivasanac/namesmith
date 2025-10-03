import uuid

import pytest

from packages.shared_py.namesmith_schemas.base import EntryPath
from services.agents.providers.local import LLMGenerationProvider, LLMScoringProvider
from services.agents.state import Candidate, GenerationInputs


@pytest.mark.asyncio
async def test_llm_generation_provider_uses_callable():
    async def fake_llm(inputs, trends, company_examples):
        return [
            {"label": "novastra", "tld": "com", "display_name": "Novastra"},
            {"label": "quantflux", "tld": "ai", "display_name": "QuantFlux"},
        ]

    provider = LLMGenerationProvider(llm_fn=fake_llm)
    inputs = GenerationInputs(
        job_id=uuid.uuid4(),
        entry_path=EntryPath.INVESTOR,
        topic="ai analytics",
        tlds=["com", "ai"],
        count=2,
    )
    candidates = await provider.generate(inputs, trends=[], company_examples=[])
    assert len(candidates) == 2
    assert all(isinstance(candidate, Candidate) for candidate in candidates)
    assert {c.full_domain for c in candidates} == {"novastra.com", "quantflux.ai"}


@pytest.mark.asyncio
async def test_llm_scoring_provider_uses_callable():
    async def fake_llm_score(candidates):
        results = []
        for candidate in candidates:
            results.append(
                {
                    "label": candidate.label,
                    "tld": candidate.tld,
                    "memorability": 7.5,
                    "pronounceability": 8.0,
                    "brandability": 9.0,
                    "overall": 8.2,
                    "rubric_version": "llm-v1",
                    "rationale": "LLM-evaluated",
                }
            )
        return results

    scoring_provider = LLMScoringProvider(llm_fn=fake_llm_score)
    candidates = [
        Candidate(label="novastra", tld="com"),
        Candidate(label="quantflux", tld="ai"),
    ]

    scored = await scoring_provider.score(candidates)
    assert len(scored) == 2
    assert all(candidate.overall == 8.2 for candidate in scored)
    assert all(candidate.rubric_version == "llm-v1" for candidate in scored)


@pytest.mark.asyncio
async def test_generation_provider_without_callable_errors():
    provider = LLMGenerationProvider()
    inputs = GenerationInputs(
        job_id=uuid.uuid4(),
        entry_path=EntryPath.INVESTOR,
        topic="ai",
        tlds=["com"],
        count=1,
    )
    with pytest.raises(RuntimeError):
        await provider.generate(inputs, trends=[], company_examples=[])


@pytest.mark.asyncio
async def test_scoring_provider_without_callable_errors():
    provider = LLMScoringProvider()
    with pytest.raises(RuntimeError):
        await provider.score([Candidate(label="novastra", tld="com")])
