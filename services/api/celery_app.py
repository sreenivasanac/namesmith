"""Celery application stub for background processing."""
from __future__ import annotations

import os

from celery import Celery

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", BROKER_URL)

celery_app = Celery("namesmith", broker=BROKER_URL, backend=RESULT_BACKEND)
celery_app.conf.update(task_default_queue="default", task_routes={})


@celery_app.task(name="namesmith.generate_job")
def run_generation_task(payload: dict) -> None:
    """Placeholder task that would dispatch the LangGraph workflow."""
    # TODO: Wire to services.agents.executor.run_generation_job with proper orchestration.
    raise NotImplementedError("Celery background processing not yet implemented")
