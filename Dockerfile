# --- Stage 1: Builder ---
# This stage installs dependencies into a virtual environment.
FROM python:3.13-slim-bookworm AS builder

# Set environment variables to prevent writing .pyc files and to buffer output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install uv, our fast package manager
RUN pip install uv

WORKDIR /app

# Copy only the pyproject.toml to leverage Docker cache
# This layer is only rebuilt if pyproject.toml changes.
COPY pyproject.toml .

# Generate a pinned requirements.txt from pyproject.toml
# This ensures deterministic builds.
RUN uv pip compile pyproject.toml -o requirements.txt

# Create a virtual environment and install dependencies into it
# This keeps our dependencies isolated and makes the final image cleaner.
RUN uv venv /opt/venv

# Install dependencies into the virtual environment using the global uv
# By pointing to the venv's python, uv knows where to install the packages.
RUN uv pip sync --python /opt/venv/bin/python requirements.txt


# --- Stage 2: Final Image ---
# This stage creates the final, lean production image.
FROM python:3.13-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Point to the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user for security
# Running as a non-root user is a critical security best practice.
RUN addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY . .

# Make scripts executable
RUN chmod +x /app/scripts/entrypoint.sh

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 4000

# The entrypoint script will run migrations first, then the CMD.
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# The command that the entrypoint will execute after it's done.
# This starts the Uvicorn server.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]