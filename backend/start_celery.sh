#!/bin/bash

# Start Celery worker for Reddit SaaS Validator

echo "🚀 Starting Celery worker..."

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Celery worker with proper config
celery -A app.celery_app worker \
    --loglevel=info \
    --queues=validation,celery \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    --hostname=validation-worker@%h

# Options explained:
# --loglevel=info: Show info logs
# --queues: Listen to validation and default queues
# --concurrency=2: Run 2 worker processes
# --max-tasks-per-child: Restart worker after 50 tasks (prevent memory leaks)
