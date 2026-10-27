FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck and judge verification)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for fast layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy full application tree
COPY . .

# Environment settings conforming to Open Agent Hackathon specification
ENV PORT=8000
ENV HOST=0.0.0.0
ENV SAMPLE_MODE=true
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Entry point
CMD ["python", "run.py", "--serve", "--port", "8000"]

