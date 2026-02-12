# 🚀 Deployment Guide: Hybrid High-Performance Infrastructure

This project uses a **Permanent Hybrid Hosting** architecture. It combines the speed of local hardware (for video processing) with the global reach of Vercel (for the UI) and Cloudflare/Upstash (for stable data).

---

## 🏗️ Architecture Overview

| Component | Provider | Role |
| :--- | :--- | :--- |
| **Frontend** | Vercel | Global Next.js UI |
| **Backend API** | Local PC + Tailscale | Permanent API Link via Funnel |
| **Worker** | Local PC | GPU/CPU Video Processing (FFmpeg) |
| **Queue/Cache** | Upstash Redis | Global Task Orchestration |
| **Database** | Supabase/Local SQLite | Persistent Data Storage |
| **Storage** | Cloudflare R2 | Global Video/Asset CDN |
| **GPU Offload** | Modal | High-tier serverless rendering |

---

## 🛠️ Phase 1: Local Backend Setup

### 1. Tailscale Funnel (Fixed Public URL)
Your backend is exposed via a permanent link. 
1. Open **Tailscale** on your PC.
2. In the terminal, run: `tailscale funnel --bg 8000`
3. Your permanent URL is: `https://desktop-ajdgsgd.tail4e4049.ts.net`

### 2. Environment Variables (`backend/.env`)
Ensure your local `.env` has these critical keys:
```env
# AI Providers
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key

# Database & Queue (Upstash)
REDIS_URL=rediss://default:...@safe-stallion-50421.upstash.io:6379

# Storage (Cloudflare R2)
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_PUBLIC_URL=https://pub-xxx.r2.dev
```

### 3. Start Services
Use the provided Pinokio dashboard or run manually:
```powershell
# Start API
python -m uvicorn app.main:app --port 8000

# Start Worker
python -m celery -A app.celery_app worker -Q video_local,celery --pool=solo
```

---

## 🌐 Phase 2: Vercel Frontend Setup

### 1. Connect GitHub
1. Push your code to your GitHub fork.
2. Import the repository into **Vercel**.

### 2. Configure Vercel Variables
In Vercel Dashboard > Settings > Environment Variables, add:
| Key | Value |
| :--- | :--- |
| `NEXT_PUBLIC_API_BASE` | `https://desktop-ajdgsgd.tail4e4049.ts.net/api` |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | (Your Stripe Key) |

> [!IMPORTANT]
> Always append `/api` to the Tailscale URL in the `NEXT_PUBLIC_API_BASE` setting.

---

## ☁️ Phase 3: External Services

### 1. Cloudflare R2 (Storage)
- Create a bucket named `proedit-storage`.
- Enable **CORS** for your Vercel URL and `localhost`.
- Set the bucket to **Public** and copy the `Public URL`.

### 2. Upstash (Redis)
- Use the **Global Redis** instance for lowest latency between Vercel and your Local PC.

### 3. Google/GitHub Auth
- Add `https://desktop-ajdgsgd.tail4e4049.ts.net/api/auth/callback/google` to your Authorized Redirect URIs in the Google Cloud Console.

---

## 🛡️ Maintenance & Monitoring

- **Logs**: If the backend is unreachable, run `tailscale funnel status` to ensure the tunnel is active.
- **Preflight (OPTIONS)**: I have configured the backend to automatically bypass rate limits and security headers for `OPTIONS` requests (CORS preflight). This ensures consistent connectivity from Vercel.
- **Quotas**: Monitor Gemini/Groq usage. If "Pro Edit Ready (degraded)" appears, your API limits are hit.
- **GPU**: If local processing is slow, the system automatically offloads to **Modal** if `MODAL_TOKEN_ID` is present.
