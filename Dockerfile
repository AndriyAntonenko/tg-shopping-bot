FROM python:3.12-slim

# Copy uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies if needed
# RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy dependency files first to leverage cache
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: sync from uv.lock
# --no-install-project: only install dependencies, not the project itself yet
RUN uv sync --frozen --no-install-project

# Copy the rest of the application
COPY src ./src
COPY main.py README.md ./

# Install the project itself
RUN uv sync --frozen

# Create data directory for SQLite
RUN mkdir -p data

# Place the virtual environment in the PATH
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "python", "main.py"]
