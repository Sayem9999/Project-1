# Deployment Guide (Vercel + Railway)

## Architecture
- **Frontend (Next.js)**: deploy `frontend/` to **Vercel**
- **Backend (FastAPI)**: deploy `backend/` to **Railway**
- **Workflow**: point `N8N_WEBHOOK_URL` to your n8n webhook endpoint

---

## 1) Deploy backend to Railway

### Required backend env vars
- `SECRET_KEY`
- `DATABASE_URL` (for production, use Postgres on Railway)
- `STORAGE_ROOT=storage`
- `N8N_WEBHOOK_URL`
- `FRONTEND_URL`
- `FRONTEND_ORIGINS` (comma-separated origins, include your Vercel URL)
- `OPENAI_API_KEY`

### CLI deployment
```bash
npm i -g @railway/cli
export RAILWAY_TOKEN=...
./scripts/deploy_railway.sh
```

`backend/railway.toml` configures start command and health checks.

---

## 2) Deploy frontend to Vercel

### Required frontend env vars on Vercel
- `NEXT_PUBLIC_API_BASE=https://<your-railway-backend-domain>/api`

### CLI deployment
```bash
export VERCEL_TOKEN=...
./scripts/deploy_vercel.sh
```

If using Vercel UI:
- Import repository
- Set **Root Directory** to `frontend`
- Add `NEXT_PUBLIC_API_BASE`

---

## 3) Post-deploy checks

1. Open frontend URL
2. Sign up and login
3. Upload sample video
4. Confirm job reaches `complete`
5. Download rendered file

---

## 4) CORS checklist

Set backend CORS to include Vercel domain:

```env
FRONTEND_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

