# syntax=docker/dockerfile:1

FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Application environment variables
# Replace these names and default values with your actual variables.
ENV TURSO_DATABASE_URL=production \
    TURSO_AUTH_TOKEN="" \
    PORT=""

WORKDIR /app

# Install Python and required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        curl \
        ca-certificates \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Verify that Python satisfies requires-python = ">=3.12"
RUN python3 --version && \
    python3 -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12 or newer is required'"

# Install Poetry
RUN python3 -m pip install \
    --no-cache-dir \
    --break-system-packages \
    poetry

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml poetry.lock* ./

# Install production dependencies
RUN poetry install \
    --only main \
    --no-root \
    --no-interaction \
    --no-ansi

# Copy the application source code
COPY . .

# Start the application
CMD ["poetry", "run", "python3", "-m", "src.sumapp"]