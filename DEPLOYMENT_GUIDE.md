# Deployment Guide (Cloud-only: Vercel + Railway)

This guide is for **production cloud deployment only**:
- **No Docker flow**
- **No local hosting flow**

## 1) Backend on Railway

Deploy directory: `backend/`

### Railway environment variables
- `SECRET_KEY`
- `DATABASE_URL` (Railway Postgres recommended)
- `STORAGE_ROOT=storage`
- `N8N_WEBHOOK_URL`
- `FRONTEND_URL`
- `FRONTEND_ORIGINS` (comma-separated, include Vercel URL)
- `OPENAI_API_KEY`

### Deploy command
```bash
export RAILWAY_TOKEN=...
./scripts/deploy_railway.sh
```

`backend/railway.toml` defines the process start command and health check.

## 2) Frontend on Vercel

Deploy directory: `frontend/`

### Vercel environment variable
- `NEXT_PUBLIC_API_BASE=https://<your-railway-domain>/api`

### Deploy command
```bash
export VERCEL_TOKEN=...
./scripts/deploy_vercel.sh
```

If using Vercel dashboard instead of CLI:
- Import repository
- Set Root Directory = `frontend`
- Add `NEXT_PUBLIC_API_BASE`

## 3) Unified deploy

For one-command cloud deployment:
```bash
export RAILWAY_TOKEN=...
export VERCEL_TOKEN=...
./scripts/deploy_cloud.sh
```

## 4) Post-deploy checks

1. Open Vercel frontend URL
2. Sign up/login
3. Upload a video
4. Confirm status reaches `complete`
5. Download rendered output

## 5) CORS checklist

Set backend CORS origins to include production frontend:

```env
FRONTEND_ORIGINS=https://your-app.vercel.app
```
