"""Entry points for running agent workflows."""
from __future__ import annotations

from datetime import datetime

from langgraph.graph.state import CompiledGraph

from services.api.db.session import SessionFactory
from services.api.repositories import get_job, update_job_status

from .graph import build_generation_graph
from .nodes.persist import build_persist_node
from .providers.local import build_default_providers
from .state import GenerationInputs, GenerationState, GenerationStateDict


async def run_generation_job(inputs: GenerationInputs) -> GenerationState:
    async with SessionFactory() as session:
        job = await get_job(session, inputs.job_id)
        start_time = datetime.utcnow()
        if job is not None:
            await update_job_status(
                session,
                job=job,
                status="running",
                started_at=start_time,
            )
            await session.commit()

        generation_provider, scoring_provider, availability_provider = build_default_providers()
        graph: CompiledGraph = build_generation_graph(
            generation_provider=generation_provider,
            scoring_provider=scoring_provider,
            availability_provider=availability_provider,
            persist_node=build_persist_node(session),
        )

        state: GenerationStateDict = {"inputs": inputs}

        try:
            final_state = await graph.ainvoke(state)
        except Exception as exc:  # noqa: BLE001
            if job is not None:
                await update_job_status(
                    session,
                    job=job,
                    status="failed",
                    error=str(exc),
                    finished_at=datetime.utcnow(),
                )
                await session.commit()
            raise

        if job is not None:
            progress = final_state.get("progress", {})
            params = dict(job.params or {})
            params["progress"] = progress
            job.params = params
            await update_job_status(
                session,
                job=job,
                status="succeeded",
                finished_at=datetime.utcnow(),
            )
            await session.commit()

        return GenerationState(**final_state)
