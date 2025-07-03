FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Copy application
COPY . .

# Create temp directory
RUN mkdir -p /tmp/video_bot && chmod 777 /tmp/video_bot

ENV PYTHONPATH=/app
ENV TEMP_DIR=/tmp/video_bot

CMD ["python", "-m", "app.main"]
