# 🚀 Step-by-Step Deployment Guide: ProEdit AI

Follow this guide to deploy the full-stack AI Video Editor with professional-grade performance and stability.

---

## 1. Prerequisites
- **GitHub Repository**: Connected to Render.com and Vercel.
- **Render.com Account**: To host the Backend and Databases.
- **Vercel Account**: To host the Frontend.
- **Cloudflare Account**: For R2 Object Storage.
- **Stripe Account**: For credit-based payments.

---

## 2. Infrastructure Setup (Render Blueprints)
The fastest way to deploy is using the `render.yaml` blueprint.

1. **New Blueprint**: Go to [Render Dashboard](https://dashboard.render.com/) -> **New** -> **Blueprint**.
2. **Connect Repo**: Select your `Project-1` repository.
3. **Approve Creation**: Render will automatically create:
   - `proedit-api` (Web Service)
   - `proedit-redis` (Redis Cache/Queue)
   - `proedit-db` (Postgres Database)
4. **Environment Variables**: Go to the `proedit-api` **Environment** tab and add these secrets:

| Key | Value Source | Required |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) | Yes |
| `R2_ACCOUNT_ID` | Cloudflare R2 Dashboard | Yes |
| `R2_ACCESS_KEY_ID` | R2 API Tokens | Yes |
| `R2_SECRET_ACCESS_KEY` | R2 API Tokens | Yes |
| `R2_BUCKET_NAME` | Name of your R2 Bucket | Yes |
| `FRONTEND_URL` | Your Vercel URL (e.g., `https://proedit.vercel.app`) | Yes |
| `STRIPE_SECRET_KEY` | Stripe Dashboard | Yes |
| `STRIPE_WEBHOOK_SECRET` | Stripe CLI/Dashboard | Yes |

---

## 3. Frontend Deployment (Vercel)
Vercel is optimized for this project's Next.js structure.

1. **Import Project**: Select the repo in Vercel.
2. **Configure Folder**: Set the **Root Directory** to `frontend`.
3. **Environment Variables**:
   - `NEXT_PUBLIC_API_BASE`: `https://proedit-api.onrender.com/api`
   - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`: From your Stripe dashboard.
4. **Deploy**: Build will complete and provide your production URL.

---

## 4. Storage Setup (Cloudflare R2)
1. **Create Bucket**: Name it `proedit-uploads`.
2. **CORS Policy**: Add this to allow the browser to upload directly:
   ```json
   [
     {
       "AllowedOrigins": ["https://your-vercel-domain.com", "http://localhost:3000"],
       "AllowedMethods": ["GET", "PUT", "POST", "HEAD"],
       "AllowedHeaders": ["*"],
       "ExposeHeaders": ["ETag"]
     }
   ]
   ```
3. **Public Access**: (Optional) Enable Public URL if you want faster direct downloads.

---

## 5. Security Hardening (Redis IP List)
We've added an `ipAllowList` placeholder in `render.yaml`. 
1. **Find your Render IP**: In Render Dashboard, find the outbound IP of the `proedit-api` service.
2. **Update render.yaml**: Replace `0.0.0.0/0` with your specific API and local dev IPs for maximum security.

---

## 6. Verification
1. **Health Check**: Visit `https://proedit-api.onrender.com/health` -> Expect `{"status": "healthy"}`.
2. **Admin Auth**: Login as an admin and visit `/admin/dashboard` to verify DB and Redis connectivity.
3. **GPU Check**: Render Web Services use CPU by default. For massive performance, upgrade the service plan to use NVIDIA GPU nodes (H100/A10G).
