# Stage 1: Build stage
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN pip install --upgrade pip setuptools wheel

# Copy project files
COPY pyproject.toml .
COPY src ./src

# Install project dependencies
# This will install the package and its dependencies into the builder stage
RUN pip install .

# Stage 2: Final stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create a non-root user
RUN useradd --create-home appuser
USER appuser

# Copy installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Copy the application code
COPY --chown=appuser:appuser src/ ./src/

# Set the entrypoint or default command if needed
# For a library, there might not be a default command.
# CMD ["python3"]