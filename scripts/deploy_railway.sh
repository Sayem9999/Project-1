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

# Deploy only the backend subtree as repository root so Railway can
# reliably resolve Docker/Nixpacks config in monorepos.
DEPLOY_PATH="$ROOT_DIR/backend"

if [ -n "${RAILWAY_SERVICE_ID:-}" ]; then
  railway up "$DEPLOY_PATH" --path-as-root --detach --ci --service "$RAILWAY_SERVICE_ID"
else
  railway up "$DEPLOY_PATH" --path-as-root --detach --ci
fi
