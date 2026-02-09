#!/usr/bin/env bash
# Start Gunicorn with 1 worker to save memory on free tier
# Timeout set to 120s for long uploads/jobs
# Start Celery worker in background (embedded mode for free tier)
celery -A app.celery_app worker --loglevel=info --concurrency 2 &

# Start Gunicorn
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app --timeout 3600
