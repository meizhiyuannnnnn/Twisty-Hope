FROM python:3.11-slim

# Use Tsinghua Debian mirror for faster downloads in China
RUN sed -i 's|http://deb.debian.org/debian|https://mirrors.tuna.tsinghua.edu.cn/debian|g' /etc/apt/sources.list.d/debian.sources

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libmagic1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (with Tsinghua mirror)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /app/uploads

# Expose API port
EXPOSE 8000

# Default command: run API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# To run the worker instead, override command:
# docker run ... backend python -m app.worker.worker
