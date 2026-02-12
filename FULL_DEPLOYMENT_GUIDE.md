# 🚀 Proedit Hybrid Deployment Guide

Follow these steps to move from Render to your super-powered Local + Cloud setup.

---

## Phase 1: Set Up Cloud Muscle (One-Time)

### 1. Modal (GPU Rendering)
- Create an account at [modal.com](https://modal.com).
- Run `modal token new` in your terminal to authenticate.
- Deploy the worker:
  ```powershell
  cd backend
  modal deploy modal_worker.py
  ```

### 2. Cloudflare R2 (Video Storage)
- Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) -> R2.
- Create a bucket named `proedit-uploads`.
- Create an **API Token** with "Edit" permissions.
- Get your `Account ID`, `Access Key`, and `Secret Key`.

---

## Phase 2: Set Up Local Hub (The Brain)

### 1. Pinokio Dashboard
- Download [Pinokio](https://pinokio.computer/).
- Click **Add** -> **Local Folder** and select the `Project-1-1` folder.
- In Pinokio, click **Install Dependencies**.

### 2. Environment Variables
- Open `backend/.env` (use the "View Settings" button in Pinokio).
- Fill in these critical keys:
  ```env
  GEMINI_API_KEY=...
  GROQ_API_KEY=...
  VERCEL_AI_GATEWAY_URL=...
  R2_ACCOUNT_ID=...
  R2_ACCESS_KEY_ID=...
  R2_SECRET_ACCESS_KEY=...
  R2_BUCKET_NAME=proedit-uploads
  ```

### 3. Start the Server
- In Pinokio, click **Start Proedit Hub (All)**.
- **Note**: If you don't see both the API and Worker terminals, you can use the **Start API Only** and **Start Worker Only** buttons in the menu.
- Ensure the API shows: `Uvicorn running on http://0.0.0.0:8000`.
- Ensure the Worker shows: `celery@... ready`.

---

## Phase 3: Go Global (Cloudflare Tunnel)

1. Open PowerShell and run: `cloudflared tunnel login`.
2. Create your tunnel: `cloudflared tunnel create proedit-api`.
3. Route it to your subdomain: `cloudflared tunnel route dns proedit-api api.yourdomain.com`.
4. Run the tunnel: `cloudflared tunnel run proedit-api --url http://localhost:8000`.

---

## Phase 4: Finalize Frontend (Vercel)

1. Go to your **Vercel Project Dashboard** -> Settings -> Environment Variables.
2. Set `NEXT_PUBLIC_API_BASE` to `https://api.yourdomain.com/api`.
3. **Redeploy** your frontend.

---

### ✅ Success Check:
Visit `https://your-vercel-domain.com`. If you can upload a video and see progress updates, your hybrid engine is officially running! 🍿🎬💎
