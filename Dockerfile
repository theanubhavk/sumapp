FROM ubuntu:latest

# Prevent interactive prompts during apt installations
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set the requested environment variables
ENV PORT=8080
ENV TURSO_DATABASE_URL=""
ENV TURSO_AUTH_TOKEN=""

# Poetry configuration
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
ENV PATH="/root/.local/bin:$PATH"

# Install Python 3.12+ (default in ubuntu:latest/24.04), pip, venv, and curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip python3-venv curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry using the official installation script
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copy dependency definition files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies (excluding dev dependencies)
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Copy the rest of the application source code
COPY . .

# Install the root project
RUN poetry install --without dev

EXPOSE $PORT

CMD ["poetry", "run", "python3", "-m", "src.sumapp"]