#!/usr/bin/env bash
set -euo pipefail

cd /app

alembic -c services/api/alembic.ini upgrade head

exec gunicorn services.api.main:app \
  --workers "${GUNICORN_WORKERS:-2}" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:${PORT:-8000}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"
