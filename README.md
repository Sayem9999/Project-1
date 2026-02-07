# edit.ai

Production-grade SaaS for professional automated video editing.

## Stack
- **Frontend:** Next.js App Router + Tailwind CSS
- **Backend:** FastAPI + REST + async SQLAlchemy
- **Workflow:** n8n webhook orchestration
- **AI:** OpenAI (GPT-4.1 + GPT-4o-mini), Whisper integration points
- **Processing:** FFmpeg on CPU
- **Auth:** Email/password + JWT

## Deploy (No Docker, No Local Hosting)

This repository is configured for:
- **Frontend on Vercel** (`frontend/`)
- **Backend on Railway** (`backend/`)

### Required secrets
- `VERCEL_TOKEN`
- `RAILWAY_TOKEN`

### One-command cloud deploy
```bash
export RAILWAY_TOKEN=...
export VERCEL_TOKEN=...
./scripts/deploy_cloud.sh
```

### Individual deploy commands
```bash
./scripts/deploy_railway.sh
./scripts/deploy_vercel.sh
```

### What else is needed to deploy successfully
- Valid `VERCEL_TOKEN` (the one provided earlier was rejected by Vercel CLI)
- Valid `RAILWAY_TOKEN`
- Railway CLI installed (`npm i -g @railway/cli`)
- Vercel CLI installed (`npm i -g vercel`)
- Outbound network access to:
  - `https://api.vercel.com`
  - `https://backboard.railway.app`
  - `https://github.com` (Railway CLI binary download)
- Recommended IDs for deterministic non-interactive deployment:
  - `RAILWAY_PROJECT_ID`
  - `RAILWAY_SERVICE_ID`
  - `VERCEL_ORG_ID`
  - `VERCEL_PROJECT_ID`

Run preflight before deploy:
```bash
./scripts/preflight_cloud.sh
```

## Production environment variables

Backend (Railway):
- `SECRET_KEY`
- `DATABASE_URL` (use Railway Postgres)
- `STORAGE_ROOT=storage`
- `N8N_WEBHOOK_URL`
- `FRONTEND_URL`
- `FRONTEND_ORIGINS` (include your Vercel domain)
- `OPENAI_API_KEY`

Frontend (Vercel):
- `NEXT_PUBLIC_API_BASE=https://<railway-backend-domain>/api`

## API surface
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/jobs/upload`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/download`
- `POST /api/workflow/n8n/callback/{job_id}`
- `POST /api/agents/{director|cutter|subtitle|audio|color|qc}`

See `DEPLOYMENT_GUIDE.md` for the full production runbook.
