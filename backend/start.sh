#!/usr/bin/env bash
# Start Gunicorn with 1 worker to save memory on free tier
# Timeout set to 120s for long uploads/jobs
# Start Celery worker in background (embedded mode for free tier)
if [[ -n "${REDIS_URL}" && ( "${REDIS_URL}" == redis://* || "${REDIS_URL}" == rediss://* ) ]]; then
  # Generate unique node name to avoid collision
  NODE_NAME="celery@${RENDER_INSTANCE_ID:-$(hostname)}"
  
  # Optimize for free tier (512MB RAM):
  # - concurrency 1: Only one task at a time
  # - max-tasks-per-child 10: Restart worker often to release memory leaks
  celery -A app.celery_app worker --loglevel=info --concurrency 1 --max-tasks-per-child 10 -n "$NODE_NAME" -Q video,celery &
else
  echo "REDIS_URL missing or invalid. Skipping Celery worker."
fi

# Start Gunicorn
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app --timeout 3600
