# edit.ai

Production-grade SaaS starter for professional automated video editing.

## Stack
- **Frontend:** Next.js App Router + Tailwind CSS
- **Backend:** FastAPI + REST + async SQLAlchemy
- **Workflow:** n8n webhook orchestration
- **AI:** OpenAI (GPT-4.1 + GPT-4o-mini), Whisper API integration points
- **Processing:** FFmpeg on CPU
- **Auth:** Email/password + JWT
- **DB:** SQLite (portable to Postgres through SQLAlchemy)
- **Storage:** Local filesystem in `backend/storage`

## Quick start

```bash
cp backend/.env.example backend/.env
# Fill SECRET_KEY and OPENAI_API_KEY

docker compose up --build
```

Frontend: `http://localhost:3000`  
Backend: `http://localhost:8000/docs`  
n8n: `http://localhost:5678`

## API surface

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/jobs/upload`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/download`
- `GET /api/jobs/storage/usage`
- `POST /api/jobs/storage/cleanup`
- `POST /api/workflow/n8n/callback/{job_id}`
- `POST /api/agents/{director|cutter|subtitle|audio|color|qc}`

## n8n orchestration
1. Backend upload route creates job and triggers webhook.
2. n8n calls status callback -> `processing`.
3. n8n executes transcript + agent decisions.
4. n8n executes FFmpeg render worker.
5. n8n posts callback with `complete` and `output_path`.

Reference workflow files:
- `docs/n8n/workflow.md`
- `docs/n8n/workflow.json`

## Environment variables

Backend (`backend/.env`):
- `SECRET_KEY`
- `DATABASE_URL`
- `STORAGE_ROOT`
- `N8N_WEBHOOK_URL`
- `FRONTEND_URL`
- `OPENAI_API_KEY`

Frontend:
- `NEXT_PUBLIC_API_BASE`


## Railway cloud deployment

Use the Railway CLI to deploy backend and frontend as separate services:

```bash
export RAILWAY_TOKEN=...
# optional deterministic routing
export RAILWAY_SERVICE_ID=...
export RAILWAY_FRONTEND_SERVICE_ID=...
./scripts/deploy_cloud_railway.sh
```

Notes:
- If `RAILWAY_SERVICE_ID` / `RAILWAY_FRONTEND_SERVICE_ID` are not set, Railway will deploy to the currently linked service for each directory.
- Run this from the repository root.

## Local deployment (no Docker required)

If Docker is unavailable, use the built-in deployment scripts:

```bash
./scripts/deploy_local.sh
```

This script will:
- create a local Python virtualenv in `.runtime/venv`
- install backend dependencies
- install and build frontend
- start backend on `:8000` and frontend on `:3000`

Stop services:

```bash
./scripts/stop_local.sh
```

Logs are stored in `.runtime/logs`.


## Local n8n callback testing

For local end-to-end testing without a full n8n instance, run the lightweight mock webhook:

```bash
python scripts/mock_n8n.py
```

It listens on `:5678/webhook/edit-ai-process`, receives backend job triggers, posts processing/complete callbacks, and writes a rendered output file.

## E2E smoke test (auth + upload + status + download)

With backend/frontend running and `scripts/mock_n8n.py` active:

```bash
python scripts/smoke_e2e.py
```

This generates a real sample video via FFmpeg, signs up a test user, uploads the video, polls job status, and downloads the final output.


## Storage lifecycle controls
- Use `GET /api/jobs/storage/usage` to inspect current storage consumption.
- Use `POST /api/jobs/storage/cleanup` to force cleanup of old R2 objects based on retention settings.
