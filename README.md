# Namesmith Backend

Python backend services for the Namesmith multi-agent domain generation system.

## Getting Started

1. Install dependencies with [uv](https://github.com/astral-sh/uv):
   ```bash
   uv sync --dev
   ```
2. Configure environment variables in `.env` (API) and `services/agents/.env` (agents). Minimum required variables:
   ```env 
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/namesmith
   ```
   The LLM-backed generation and WhoAPI availability providers require:
   ```env
   OPENAI_API_KEY=sk-...
   WHOAPI_API_KEY=your-whoapi-token
   WHOISJSON_API_KEY=your-whoisjson-api-token
   ```
3. Run the API locally:
   ```bash
   uv run uvicorn services.api.main:app --reload
   ```
4. Trigger the agent directly for manual testing:
   ```bash
   uv run python -m services.agents.run_local --topic "ai analytics" --count 5
   ```
5. Start the web frontend for local development:
   ```bash
   pnpm --dir apps/web dev
   ```

The API automatically schedules the LangGraph agent when `/v1/jobs/generate` is called.

## Tests

Run the unit tests with:
```bash
uv run pytest
```

## Project Structure

- `services/api`: FastAPI app, SQLAlchemy models, Alembic migrations, Celery stub.
- `services/agents`: LangGraph workflow, providers, and executor running against the shared database.
- `packages/shared_py`: Pydantic schemas shared across services.
- `tests`: Fast unit tests for providers and serializers.

## TODO

- Implement Supabase JWT verification for `Authorization` headers.
- Wire Celery worker to execute long-running jobs outside the API process.
