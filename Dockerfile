FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

    # Copy requirements first for caching
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Clean any existing .chainlit to avoid stale/outdated config
    RUN rm -rf /app/.chainlit

    # Copy application
    COPY app.py .

    EXPOSE 7860

    ENV CHAINLIT_TELEMETRY_ENABLED=false
    ENV PORT=7860

    CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860", "--headless"]