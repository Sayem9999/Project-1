#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
RUNTIME_DIR="$ROOT_DIR/.runtime"
LOG_DIR="$RUNTIME_DIR/logs"
PID_DIR="$RUNTIME_DIR/pids"

mkdir -p "$LOG_DIR" "$PID_DIR" "$BACKEND_DIR/storage/uploads" "$BACKEND_DIR/storage/outputs"

if [ ! -f "$BACKEND_DIR/.env" ]; then
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
fi
python - <<'PY'
from pathlib import Path
p = Path('backend/.env')
text = p.read_text()
if 'SECRET_KEY=change-me' in text:
    text = text.replace('SECRET_KEY=change-me', 'SECRET_KEY=local-dev-secret-key')
p.write_text(text)
PY

python -m venv "$RUNTIME_DIR/venv"
source "$RUNTIME_DIR/venv/bin/activate"
pip install --upgrade pip >/dev/null
pip install -r "$BACKEND_DIR/requirements.txt" >/dev/null

npm --prefix "$FRONTEND_DIR" install >/dev/null
npm --prefix "$FRONTEND_DIR" run build >/dev/null

./scripts/stop_local.sh >/dev/null 2>&1 || true

nohup bash -lc "cd '$BACKEND_DIR' && '$RUNTIME_DIR/venv/bin/uvicorn' app.main:app --host 0.0.0.0 --port 8000" >"$LOG_DIR/backend.log" 2>&1 &
nohup bash -lc "cd '$FRONTEND_DIR' && HOSTNAME=0.0.0.0 PORT=3000 npm run start" >"$LOG_DIR/frontend.log" 2>&1 &

for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null; then
    break
  fi
  sleep 1
done
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:3000 >/dev/null; then
    break
  fi
  sleep 1
done

if ! curl -fsS http://127.0.0.1:8000/health >/dev/null; then
  echo "Backend failed to start"
  tail -n 120 "$LOG_DIR/backend.log" || true
  exit 1
fi
if ! curl -fsS http://127.0.0.1:3000 >/dev/null; then
  echo "Frontend failed to start"
  tail -n 120 "$LOG_DIR/frontend.log" || true
  exit 1
fi

backend_pid="$(pgrep -f "uvicorn app.main:app --host 0.0.0.0 --port 8000" | tail -n 1 || true)"
frontend_pid="$(pgrep -f "next start" | tail -n 1 || true)"

if [ -z "$backend_pid" ] || ! kill -0 "$backend_pid" 2>/dev/null; then
  echo "Could not detect a live backend PID after startup"
  exit 1
fi
if [ -z "$frontend_pid" ] || ! kill -0 "$frontend_pid" 2>/dev/null; then
  echo "Could not detect a live frontend PID after startup"
  exit 1
fi
printf '%s' "$backend_pid" > "$PID_DIR/backend.pid"
printf '%s' "$frontend_pid" > "$PID_DIR/frontend.pid"

echo "Deployment started"
echo "Backend PID: $backend_pid"
echo "Frontend PID: $frontend_pid"
