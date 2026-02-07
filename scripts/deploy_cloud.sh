#!/usr/bin/env bash
set -euo pipefail

if [ -z "${RAILWAY_TOKEN:-}" ] || [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "Both RAILWAY_TOKEN and VERCEL_TOKEN are required."
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT_DIR/scripts/deploy_railway.sh"
"$ROOT_DIR/scripts/deploy_vercel.sh"

echo "Cloud deployment commands executed for Railway and Vercel."
