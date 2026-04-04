# Use Python 3.11 slim — lighter and more current than 3.10
FROM python:3.11-slim

WORKDIR /app

# System deps needed by PyMuPDF and file detection
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clear stale chainlit config
RUN rm -rf /app/.chainlit

# Copy app files (chainlit.md is needed for the welcome message)
COPY app.py .
COPY chainlit.md .

EXPOSE 7860

ENV CHAINLIT_TELEMETRY_ENABLED=false
ENV PORT=7860

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860", "--headless"]