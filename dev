#!/usr/bin/env bash

set -e

cleanup() {
  kill "$backend_pid" 2>/dev/null || true
  wait "$backend_pid" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

uv run --project backend uvicorn data_agent.api:app \
  --host 127.0.0.1 \
  --port 8000 \
  --reload &

backend_pid=$!

pnpm --dir frontend dev
