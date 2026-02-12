# OCI One-Command Deploy (Backend + Worker + Redis + Ollama + Caddy)

This deploy path targets: **Oracle Cloud (Ubuntu 22.04)** with **Vercel frontend**.

Goals:
- Backend is public over HTTPS (Caddy).
- Ollama is **localhost-only** on the VM (no public `11434`).
- Worker runs as a systemd service.
- Redis runs locally.

## 0. Prereqs
- An OCI Compute instance (Ubuntu 22.04).
- Ports open in OCI security list:
  - Inbound: `22` (SSH), `80` and `443` (Caddy)
  - Outbound: allow all (default)
- A domain name pointing to your VM public IP (recommended), or use `sslip.io`.

## 1. SSH in
```bash
ssh ubuntu@YOUR_VM_PUBLIC_IP
```

## 2. Run bootstrap (single command)
This installs packages, Redis, Ollama, clones repo, creates venv, and writes systemd units.

```bash
curl -fsSL https://raw.githubusercontent.com/Sayem9999/Project-1/main/deploy/oci/bootstrap.sh | bash
```

## 3. Configure environment
Edit:
```bash
sudo nano /opt/proedit/backend/.env
```

Minimum required:
- `ENVIRONMENT=production`
- `SECRET_KEY=...`
- `REDIS_URL=redis://127.0.0.1:6379`
- `DATABASE_URL=sqlite+aiosqlite:///./storage/edit_ai.db` (ok to start) or Postgres
- `FRONTEND_URL=https://YOUR_VERCEL_APP.vercel.app`
- `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `LLM_PRIMARY_PROVIDER=ollama`

## 4. Configure Caddy domain
Edit:
```bash
sudo nano /etc/caddy/Caddyfile
```

Set:
```caddy
YOUR_DOMAIN {
  reverse_proxy 127.0.0.1:8000
}
```

Then:
```bash
sudo systemctl restart caddy
```

## 5. Start services
```bash
sudo systemctl enable --now proedit-api
sudo systemctl enable --now proedit-worker
sudo systemctl status proedit-api --no-pager
sudo systemctl status proedit-worker --no-pager
```

Health:
```bash
curl https://YOUR_DOMAIN/health
```

## 6. Vercel env
Set on Vercel:
- `NEXT_PUBLIC_API_BASE=https://YOUR_DOMAIN/api`

