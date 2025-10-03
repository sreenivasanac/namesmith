"""Persistence node that writes agent outputs to the database."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from services.api.repositories import (
    link_domain_to_job,
    record_agent_run,
    upsert_availability,
    upsert_domain,
    upsert_evaluation,
)

from ..settings import settings
from ..state import AvailabilityResult, GenerationStateDict, ScoredCandidate


def build_persist_node(session: AsyncSession):
    async def _persist(state: GenerationStateDict) -> dict[str, list[str]]:
        job_id = state["inputs"].job_id
        agent_name = settings.generation_model
        timestamp = datetime.utcnow()

        scored: Iterable[ScoredCandidate] = state.get("scored") or state.get("filtered") or []
        availability_map = {
            result.full_domain: result for result in state.get("availability", [])
        }

        domain_ids: list[str] = []
        for candidate in scored:
            domain = await upsert_domain(
                session,
                label=candidate.label,
                tld=candidate.tld,
                display_name=candidate.display_name,
                processed_by_agent=settings.generation_model,
                agent_model=settings.generation_model,
            )
            availability = availability_map.get(candidate.full_domain)
            if availability:
                await upsert_availability(
                    session,
                    domain_id=domain.id,
                    status=availability.status,
                    processed_by_agent=settings.generation_model,
                    agent_model=settings.generation_model,
                    registrar=availability.registrar,
                    method="registrar",
                    raw_payload=None,
                    ttl_sec=None,
                )
            await upsert_evaluation(
                session,
                domain_id=domain.id,
                possible_categories=[],
                possible_keywords=[],
                memorability_score=int(round(candidate.memorability)),
                pronounceability_score=int(round(candidate.pronounceability)),
                brandability_score=int(round(candidate.brandability)),
                overall_score=int(round(candidate.overall)),
                description=candidate.rationale or "Generated via heuristic scoring.",
                processed_by_agent=settings.generation_model,
                agent_model=settings.generation_model,
            )
            domain_ids.append(str(domain.id))
            await link_domain_to_job(session, job_id=job_id, domain_id=domain.id)

        await record_agent_run(
            session,
            job_id=job_id,
            agent_name=agent_name,
            status="succeeded",
            input_payload=state["inputs"].model_dump(),
            output_payload={
                "count": len(domain_ids),
            },
            started_at=timestamp,
            finished_at=datetime.utcnow(),
        )
        await session.commit()
        progress = dict(state.get("progress", {}))
        progress["persisted"] = len(domain_ids)
        return {"persisted_domain_ids": domain_ids, "progress": progress}

    return _persist
