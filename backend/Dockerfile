FROM python:3.12-slim

# Timezone for the notification scheduler: reminders fire at the configured
# HH:MM in this zone, and the heute/gestern wording is computed in it too.
# The compose file overrides this via the TZ environment variable.
# (python:3.12-slim already ships tzdata, so no extra packages are needed.)
ENV TZ=Europe/Berlin

WORKDIR /app

# Install uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock* ./

# Install production dependencies (no dev extras)
RUN uv sync --no-dev --no-editable

# Copy application source
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Run Alembic migrations then start the server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
