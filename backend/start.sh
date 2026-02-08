#!/usr/bin/env bash
# Start Gunicorn with 1 worker to save memory on free tier
# Timeout set to 120s for long uploads/jobs
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:10000 app.main:app --timeout 3600
