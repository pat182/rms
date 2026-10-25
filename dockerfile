FROM python:3.15-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini ./
COPY docker-entrypoint.sh ./

RUN chmod +x /app/docker-entrypoint.sh \
    && mkdir -p /app/uploads

EXPOSE 8000

CMD ["/app/docker-entrypoint.sh"]