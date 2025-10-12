## Agent workflow orchestration notes

- **Current behavior:** the `/v1/jobs/generate` endpoint validates the request, creates a `jobs` row, and immediately schedules the LangGraph execution with `asyncio.create_task`. The task runs fully within the API process and updates the job record when finished. This keeps latency low for short LLM calls (≈1–2 seconds) and avoids Celery startup overhead during early development.
- **Future direction:** once we add longer-running steps (extended research, large availability batches, or human-in-the-loop checkpoints) we will hand jobs to Celery workers via `services/api/celery_app.py`. The API will enqueue the task and return a job id for polling while workers update progress fields.
- **Hybrid approach:** any step that can finish well within the HTTP timeout (e.g., a small LLM prompt) should remain in-process for responsiveness. Steps that might exceed the timeout or require retries/backoff should be moved to Celery queues. We will later.
- **Next actions:** keep tracking job durations in `jobs.params.progress`. When we integrate Celery, reuse the same persistence functions so the console experience remains consistent.
