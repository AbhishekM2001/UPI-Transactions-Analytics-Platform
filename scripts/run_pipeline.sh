#!/bin/bash
set -e  # Exit on error

echo "=== Starting Pipeline ==="

# Run services sequentially
docker-compose run --remove-orphans scrape && \
docker-compose run --remove-orphans clean && \
docker-compose run --remove-orphans upload && \
docker-compose run --remove-orphans refresh

echo "=== Pipeline Completed ==="