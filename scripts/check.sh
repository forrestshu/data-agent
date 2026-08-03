#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

uv run --project "$project_root/backend" python -m unittest discover -s "$project_root/backend/tests"
uv run --project "$project_root/backend" python -m unittest discover -s "$project_root/tests" -p "test_*.py"
pnpm --dir "$project_root/frontend" exec tsc --noEmit
docker compose -f "$project_root/docker/docker-compose.yml" config --quiet
