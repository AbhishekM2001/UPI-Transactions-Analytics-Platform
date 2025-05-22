FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pinned versions first
COPY requirements.txt .
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    pandas==1.5.3

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .