# syntax=docker/dockerfile:1

FROM node:24-bookworm-slim AS frontend-build

WORKDIR /build/frontend

RUN corepack enable \
    && corepack prepare pnpm@10.32.1 --activate

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend/index.html ./
COPY frontend/tsconfig*.json ./
COPY frontend/vite.config.ts ./
COPY frontend/public ./public
COPY frontend/src ./src
RUN pnpm build


FROM python:3.12-slim-bookworm AS python-build

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN python -m pip install --no-cache-dir uv==0.10.10

WORKDIR /app/backend

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/src ./src
RUN uv sync --frozen --no-dev


FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/app/backend/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

RUN apt-get update \
    && apt-get install -y --no-install-recommends libltdl7 libkrb5-3 libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=python-build /app/backend/.venv ./backend/.venv
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
COPY backend/src ./backend/src
COPY data/sqlite/data-agent-2026-7-15.sqlite ./data/sqlite/data-agent-2026-7-15.sqlite

RUN groupadd --gid 10001 data-agent \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin data-agent \
    && mkdir -p /app/.data-agent \
    && chown -R data-agent:data-agent \
        /app/.data-agent \
        /app/backend/src/data_agent/semantic_layer

USER data-agent

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"]

CMD ["uvicorn", "data_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
