# Python build stage for dependencies via uv
FROM python:3.13-slim AS pythonbuilder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_NO_INTERACTION=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_CACHE_DIR=/tmp/uv_cache

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --locked --no-install-project --no-dev && rm -rf $UV_CACHE_DIR

# Node build stage for static assets
FROM node:22.21-slim AS nodebuilder

WORKDIR /app

COPY . .

RUN npm install

RUN npm run build

# Final runtime stage
FROM python:3.13-slim AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=pythonbuilder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY . .

COPY --from=nodebuilder /app/src_compiled ./src_compiled

EXPOSE 8000