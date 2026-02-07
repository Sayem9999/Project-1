#!/usr/bin/env bash
set -euo pipefail

if ! command -v railway >/dev/null 2>&1; then
  echo "Railway CLI not found. Install with: npm i -g @railway/cli"
  exit 1
fi

if [ -z "${RAILWAY_TOKEN:-}" ]; then
  echo "RAILWAY_TOKEN is required for non-interactive deploy"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"

if [ -n "${RAILWAY_PROJECT_ID:-}" ] && [ -n "${RAILWAY_SERVICE_ID:-}" ]; then
  railway up --detach --ci --service "$RAILWAY_SERVICE_ID"
else
  railway up --detach --ci
fi
