#!/usr/bin/env bash
# Start Gunicorn with 1 worker to save memory on free tier
# Timeout set to 120s for long uploads/jobs
# Celery runs in a separate Render worker service.
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app --timeout 3600
