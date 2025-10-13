
- Authentication is currently implemented as a lightweight placeholder that accepts a UUID bearer token. Replace `services/api/auth.py` with a Supabase JWT verifier when keys are available.
- LiteLLM credentials for any allowlisted models (OpenAI, Anthropic, etc.) will be provided via environment variables so runtime calls succeed without additional per-provider SDK wiring. Check if LiteLLM needs API Key / credentials.
- Job orchestration executes LangGraph workflows inside the API process via `asyncio.create_task`. The Celery stub (`services/api/celery_app.py`) remains future background worker adoption; see `agentic_development_docs/agent_communication/workflow_orchestration.md` for the current vs. planned flow.
- Context gathering is still a placeholder that tokenizes the topic/prompt; future work needs to replace it with real trend and company lookups.
- Unit tests now cover the LLM generation/scoring providers; database integration tests remain blocked pending a dedicated Postgres test fixture.
- TODO: Replace the placeholder context gatherer with investor-specific retrieval that leverages provider-backed trend, similar companies fetching logic and company lookups.
