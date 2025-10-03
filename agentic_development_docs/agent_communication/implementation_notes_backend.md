# Backend Implementation Notes (Agents + API)

- Authentication is currently implemented as a lightweight placeholder that accepts a UUID bearer token. Replace `services/api/auth.py` with a Supabase JWT verifier when keys are available.
- Domain availability checks default to the stub provider unless a WhoAPI key is provided. The provider scaffolding (`WhoapiAvailabilityProvider`) is ready for integration once credentials are supplied.
- Job orchestration executes LangGraph workflows inside the API process via `asyncio.create_task`. The Celery stub (`services/api/celery_app.py`) is included for the future move to background workers.
- Generated domains are associated back to their originating jobs through the `job_domain_links` join table so user ownership (via `jobs.created_by`) remains traceable.
- Each completed agent run records progress metrics on the `jobs.params` column; the job endpoints surface these in their responses so the console can display live counters.
- Unit tests target the heuristic generation/scoring providers and serialization layer. Database integration tests are pending until a dedicated Postgres test fixture is available.
- Providers now assume LLM-backed generation and scoring (`LLMGenerationProvider`, `LLMScoringProvider`). Inject callable shims that talk to your preferred LLM before running the pipeline; otherwise the providers raise explicit configuration errors.
