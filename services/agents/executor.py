"""Entry points for running agent workflows."""
from __future__ import annotations

from datetime import datetime

# TODO check if this can be made into ONE recent version only
try:  # pragma: no cover - compatibility shim across langgraph versions
    from langgraph.graph.state import CompiledGraph
except ImportError:  # noqa: WPS433
    from langgraph.graph.state import CompiledStateGraph as CompiledGraph

from services.api.db.session import SessionFactory
from services.api.repositories import get_job, update_job_status

from .graph import build_generation_graph
from .settings import settings
from .nodes.persist import build_persist_node
from .providers.llm import build_default_providers
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
        # TODO check if this code can be made simpler, remove try catch, remove if else

        resolved_generation_model: str | None = None
        resolved_scoring_model: str | None = None
        resolved_inputs: GenerationInputs
        try:
            resolved_generation_model = inputs.generation_model or settings.generation_model
            resolved_scoring_model = inputs.scoring_model or settings.scoring_model

            allowlist = settings.model_allowlist
            if allowlist:
                if resolved_generation_model not in allowlist:
                    raise ValueError(f"Generation model '{resolved_generation_model}' is not permitted")
                if resolved_scoring_model not in allowlist:
                    raise ValueError(f"Scoring model '{resolved_scoring_model}' is not permitted")

            resolved_inputs = inputs.model_copy(
                update={
                    "generation_model": resolved_generation_model,
                    "scoring_model": resolved_scoring_model,
                }
            )

            generation_provider, scoring_provider, availability_provider = build_default_providers(
                generation_model=resolved_generation_model,
                scoring_model=resolved_scoring_model,
            )
            graph: CompiledGraph = build_generation_graph(
                generation_provider=generation_provider,
                scoring_provider=scoring_provider,
                availability_provider=availability_provider,
                persist_node=build_persist_node(session),
            )

            state: GenerationStateDict = {"inputs": resolved_inputs}
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

        assert resolved_generation_model is not None and resolved_scoring_model is not None

        if job is not None:
            progress = final_state.get("progress", {})
            params = dict(job.params or {})
            params["generation_model"] = resolved_generation_model
            params["scoring_model"] = resolved_scoring_model
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
