# Deployment Guide (Cloud-only: Vercel + Railway)

This guide is for **production cloud deployment only**:
- **No Docker flow**
- **No local hosting flow**

## 0) Preflight (required)

Before deploying, run:

```bash
./scripts/preflight_cloud.sh
```

This checks:
- required tokens
- required CLIs
- required network reachability

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

### Recommended deployment identifiers
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `RAILWAY_PROJECT_ID`
- `RAILWAY_SERVICE_ID`

### Deploy command
```bash
export VERCEL_TOKEN=...
./scripts/deploy_vercel.sh
```

If using Vercel dashboard instead of CLI:
- Import repository
- Add `NEXT_PUBLIC_API_BASE`

This repo includes a root `vercel.json` that builds `frontend/package.json` to avoid root-level 404 deployments in monorepos.

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


## 6) Alternative: Deploy frontend on Railway (no Vercel)

Use this if you want to avoid Vercel entirely.

### Frontend deploy command
```bash
export RAILWAY_TOKEN=...
./scripts/deploy_frontend_railway.sh
```

### Deploy both backend + frontend on Railway
```bash
export RAILWAY_TOKEN=...
./scripts/deploy_cloud_railway.sh
```

### Required IDs for deterministic deploys
- `RAILWAY_SERVICE_ID` (backend)
- `RAILWAY_FRONTEND_SERVICE_ID` (frontend)
