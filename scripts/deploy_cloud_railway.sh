#!/usr/bin/env bash
set -euo pipefail

if [ -z "${RAILWAY_TOKEN:-}" ]; then
  echo "RAILWAY_TOKEN is required"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT_DIR/scripts/deploy_railway.sh"
"$ROOT_DIR/scripts/deploy_frontend_railway.sh"

echo "Railway backend + frontend deployment commands executed."
