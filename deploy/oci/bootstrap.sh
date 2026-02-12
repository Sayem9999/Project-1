#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/proedit"
REPO_URL="https://github.com/Sayem9999/Project-1.git"

echo "[1/8] Installing OS packages..."
sudo apt-get update -y
sudo apt-get install -y \
  git curl ca-certificates \
  python3.11 python3.11-venv \
  ffmpeg \
  redis-server \
  caddy

echo "[2/8] Enabling Redis..."
sudo systemctl enable --now redis-server

echo "[3/8] Installing Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
sudo systemctl enable --now ollama

echo "[4/8] Pulling default model (llama3.2:3b)..."
ollama pull llama3.2:3b || true

echo "[5/8] Cloning repo to ${APP_DIR}..."
if [ -d "${APP_DIR}/.git" ]; then
  sudo git -C "${APP_DIR}" pull --ff-only
else
  sudo rm -rf "${APP_DIR}"
  sudo git clone "${REPO_URL}" "${APP_DIR}"
fi

echo "[6/8] Creating backend venv + installing deps..."
sudo bash -lc "cd '${APP_DIR}/backend' && python3.11 -m venv .venv"
sudo bash -lc "cd '${APP_DIR}/backend' && . .venv/bin/activate && pip install -r requirements.txt"

echo "[7/8] Writing systemd units..."
sudo cp -f "${APP_DIR}/deploy/oci/systemd/proedit-api.service" /etc/systemd/system/proedit-api.service
sudo cp -f "${APP_DIR}/deploy/oci/systemd/proedit-worker.service" /etc/systemd/system/proedit-worker.service
sudo systemctl daemon-reload

echo "[8/8] Writing default Caddyfile..."
if [ ! -f /etc/caddy/Caddyfile ] || ! grep -q "proedit-api" /etc/caddy/Caddyfile; then
  sudo cp -f "${APP_DIR}/deploy/oci/Caddyfile.example" /etc/caddy/Caddyfile
  sudo systemctl enable --now caddy
  sudo systemctl restart caddy || true
fi

echo
echo "Bootstrap complete."
echo "- App path: ${APP_DIR}"
echo "- Next:"
echo "  1) Edit backend env: sudo nano ${APP_DIR}/backend/.env"
echo "  2) Edit Caddy domain: sudo nano /etc/caddy/Caddyfile"
echo "  3) Start services:"
echo "     sudo systemctl enable --now proedit-api"
echo "     sudo systemctl enable --now proedit-worker"

