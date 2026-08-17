#!/usr/bin/env bash
# Start the application in development mode
set -euo pipefail

PORT="${PORT:-8000}"

# Prefer the project venv if present
if [ -x ".venv/bin/python" ]; then
  PY="${PYTHON:-$PWD/.venv/bin/python}"
else
  PY="${PYTHON:-python}"
fi

echo "Starting Real Estate AI Agent..."

# Start Redis if not running
if ! redis-cli ping >/dev/null 2>&1; then
  echo "Starting Redis..."
  docker run -d -p 6379:6379 redis:7-alpine 2>/dev/null || true
  sleep 2
fi

# Start the application
echo "Starting FastAPI server on port $PORT..."
"$PY" -m uvicorn app.api:app --host 0.0.0.0 --port "$PORT" --reload
