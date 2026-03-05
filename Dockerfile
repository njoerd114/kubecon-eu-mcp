FROM python:3.14-slim

WORKDIR /app

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN uv pip install --system .

# Expose port for Streamable HTTP transport
EXPOSE 8000

# Run in HTTP mode for hosted deployment
CMD ["kubecon-eu-mcp", "--http"]
