# Deployment Handoff Guide

Your ProEdit system is polished, tested, and ready for deployment. Follow these steps to take it live.

## 1. Backend Hosting (Hybrid Local)

Your backend runs on your high-performance local PC, exposed securely via Tailscale.

**Step 1: Ensure Backend is Running**
You should already have the production backend running from our tests. If not:
```powershell
# In terminal 1
cd backend
./start_production_local.ps1
```

**Step 2: Start Tailscale Funnel**
Expose port 8000 to the public internet securely (HTTPS).
```powershell
# In terminal 2 (if not already running)
tailscale funnel --bg 8000
```
*Note the public URL provided by Tailscale (e.g., `https://your-machine.tail-name.ts.net`).*

**Step 3: Start Celery Worker**
Process video jobs in the background.
```powershell
# In terminal 3
cd backend
./run_worker.ps1
```

## 2. Frontend Hosting (Vercel)

Deploy the Next.js frontend to Vercel for global edge delivery.

**Step 1: Push Code to GitHub**
Ensure your latest changes (including type fixes) are committed and pushed.
```bash
git add .
git commit -m "feat: production polish and type safety"
git push origin main
```

**Step 2: Import Project in Vercel**
1.  Go to dashboard.vercel.com
2.  "Add New..." -> "Project"
3.  Import your Git repository.
4.  **Framework Preset**: Next.js
5.  **Root Directory**: `frontend` (Important!)

**Step 3: Environment Variables**
Configure these in Vercel Project Settings:

| Variable | Value | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_BASE` | `https://your-machine.tail-name.ts.net/api` | Your Tailscale Funnel URL |

**Step 4: Deploy**
Click "Deploy". Vercel will build and launch your site.

## 3. Post-Deployment Verification

1.  Visit your Vercel URL (e.g., `https://project-1.vercel.app`).
2.  Login with your admin account.
3.  Upload a test video.
4.  Watch the "Hollywood Pipeline" real-time visualization.
5.  Verify the video completes and plays back.

v
## Troubleshooting

*   **Tailscale Error 502**: Ensure `start_production_local.ps1` is running on port 8000.
*   **CORS Error**: Update `backend/app/main.py` -> `allow_origins` to include your new Vercel domain if not already covered by regex.
