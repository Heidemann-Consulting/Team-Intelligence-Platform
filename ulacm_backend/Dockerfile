# File: ulacm_backend/Dockerfile
# Purpose: Builds the Docker image for the FastAPI backend application.
# Uvicorn command will be overridden in docker-compose.yml for SSL.

# --- Base Stage ---
# Use an official Python runtime as a parent image
# Using a specific version is recommended for reproducibility
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 [cite: 75]

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install system dependencies if needed (e.g., for psycopg2 build)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install poetry (or pip if using requirements.txt)
# Using pip for simpler Docker layer caching if preferred over poetry install
RUN pip install --upgrade pip
RUN pip install poetry==1.8.2 # Use a specific version of Poetry

# --- Builder Stage (for installing dependencies) ---
FROM base as builder

# Copy only dependency definition files first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install project dependencies using Poetry
# --no-root: install only dependencies, not the project itself yet
# --no-dev: exclude development dependencies
# --no-interaction: disable interactive prompts
# --no-ansi: disable ANSI output for cleaner logs
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev --no-interaction --no-ansi

# --- Final Stage ---
FROM base as final

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code into the container
COPY . /app

# Expose the port the app runs on (defined in uvicorn command or env var)
# Default FastAPI port is 8000 for HTTP, 8443 for HTTPS (example)
EXPOSE 8000
EXPOSE 8443

# Command to run the application using Uvicorn
# Use environment variables for host and port for flexibility
# Ensure the host is 0.0.0.0 to accept connections from outside the container
# Use reload flag only for development, not production
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] # Development command
# The actual command for production (with SSL) will be provided in docker-compose.yml
# This CMD serves as a fallback if not overridden.
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
