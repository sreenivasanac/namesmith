import json
import uuid

import pytest

from packages.shared_py.namesmith_schemas.base import EntryPath
from services.agents.providers import llm
from services.agents.providers.llm import LLMGenerationProvider, LLMScoringProvider
from services.agents.state import Candidate, GenerationInputs


@pytest.mark.asyncio
async def test_llm_generation_provider_uses_litellm(monkeypatch):
    captured: dict[str, str] = {}

    async def fake_acompletion(**kwargs):
        captured.update(kwargs)
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            [
                                {"label": "novastra", "tld": "com", "display_name": "Novastra"},
                                {"label": "quantflux", "tld": "ai", "display_name": "QuantFlux"},
                            ]
                        )
                    }
                }
            ]
        }

    monkeypatch.setattr(llm, "acompletion", fake_acompletion)

    provider = LLMGenerationProvider(model_name="stub-model")
    inputs = GenerationInputs(
        job_id=uuid.uuid4(),
        entry_path=EntryPath.INVESTOR,
        topic="ai analytics",
        tlds=["com", "ai"],
        count=2,
    )
    candidates = await provider.generate(inputs, trends=[], company_examples=[])

    assert {c.full_domain for c in candidates} == {"novastra.com", "quantflux.ai"}
    assert captured["model"] == "stub-model"


@pytest.mark.asyncio
async def test_llm_scoring_provider_uses_litellm(monkeypatch):
    async def fake_acompletion(**kwargs):
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            [
                                {
                                    "label": "novastra",
                                    "tld": "com",
                                    "memorability": 8,
                                    "pronounceability": 8,
                                    "brandability": 9,
                                    "overall": 8,
                                    "rubric_version": "llm-v1",
                                    "rationale": "LLM-evaluated",
                                },
                                {
                                    "label": "quantflux",
                                    "tld": "ai",
                                    "memorability": 7,
                                    "pronounceability": 8,
                                    "brandability": 8,
                                    "overall": 8,
                                    "rubric_version": "llm-v1",
                                    "rationale": "LLM-evaluated",
                                },
                            ]
                        )
                    }
                }
            ]
        }

    monkeypatch.setattr(llm, "acompletion", fake_acompletion)

    scoring_provider = LLMScoringProvider(model_name="stub-model")
    candidates = [
        Candidate(label="novastra", tld="com"),
        Candidate(label="quantflux", tld="ai"),
    ]

    scored = await scoring_provider.score(candidates)
    assert len(scored) == 2
    assert scored[0].overall == 8
    assert scored[0].rubric_version == "llm-v1"


@pytest.mark.asyncio
async def test_generation_provider_invalid_json(monkeypatch):
    async def fake_acompletion(**kwargs):
        return {"choices": [{"message": {"content": "not json"}}]}

    monkeypatch.setattr(llm, "acompletion", fake_acompletion)

    provider = LLMGenerationProvider(model_name="stub-model")
    inputs = GenerationInputs(
        job_id=uuid.uuid4(),
        entry_path=EntryPath.INVESTOR,
        topic="ai",
        tlds=["com"],
        count=1,
    )
    with pytest.raises(ValueError):
        await provider.generate(inputs, trends=[], company_examples=[])
