# Backend Implementation Notes (Agents + API)

- Authentication is currently implemented as a lightweight placeholder that accepts a UUID bearer token. Replace `services/api/auth.py` with a Supabase JWT verifier when keys are available.
- Domain availability checks default to the probabilistic stub provider unless registrar credentials are configured. WhoisJSON (`WhoisJsonAvailabilityProvider`) is the preferred real provider, with WhoAPI available as an alternative; enable them by setting the corresponding API key environment variables.
- Job orchestration executes LangGraph workflows inside the API process via `asyncio.create_task`. The Celery stub (`services/api/celery_app.py`) remains ready for future background worker adoption; see `agentic_development_docs/agent_communication/workflow_orchestration.md` for the current vs. planned flow.
- Generated domains are associated back to their originating jobs through the `job_domain_links` join table so user ownership (via `jobs.created_by`) remains traceable.
- Each completed agent run records progress metrics on the `jobs.params` column; the job endpoints surface these in their responses so the console can display live counters.
- Context gathering is still a placeholder that tokenizes the topic/prompt; future work needs to replace it with real trend and company lookups.
- Unit tests now cover the LLM generation/scoring providers; database integration tests remain blocked pending a dedicated Postgres test fixture.
- LLM generation and scoring run through LiteLLM with JSON-only prompts. Model names are chosen per job, validated with `settings.model_allowlist`, and persisted in `jobs.params` so API responses expose the active configuration.
- TODO: Add Langfuse and Sentry instrumentation once observability requirements are prioritized.
