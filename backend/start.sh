#!/usr/bin/env bash
# Start Gunicorn with 1 worker to save memory on free tier.
# Celery is disabled by default on web instances. Enable only for local/dev with:
#   RUN_EMBEDDED_CELERY=true
# Determine queue (match settings default)
QUEUE_NAME="${CELERY_VIDEO_QUEUE:-video}"

if [[ "${RUN_EMBEDDED_CELERY:-false}" == "true" ]] && [[ -n "${REDIS_URL}" && ( "${REDIS_URL}" == redis://* || "${REDIS_URL}" == rediss://* ) ]]; then
  # Generate unique node name to avoid collision
  NODE_NAME="celery@${RENDER_INSTANCE_ID:-$(hostname)}"
  
  # Optimize for free tier (512MB RAM):
  # - concurrency 1: Only one task at a time
  # - solo pool: avoid prefork memory overhead
  # - disable gossip/mingle/heartbeat to reduce broker chatter and memory
  celery -A app.celery_app worker \
    --loglevel=info \
    --pool=solo \
    --concurrency=1 \
    --without-gossip \
    --without-mingle \
    --without-heartbeat \
    -n "$NODE_NAME" \
    -Q "$QUEUE_NAME,celery" &
else
  echo "Embedded Celery disabled or REDIS_URL missing. Running API-only mode."
fi

# Start Gunicorn
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app --timeout 3600
