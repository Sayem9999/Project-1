#!/usr/bin/env bash
set -euo pipefail

missing=0

check_env() {
  local key="$1"
  if [ -z "${!key:-}" ]; then
    echo "Missing required env var: $key"
    missing=1
  fi
}

check_cmd() {
  local cmd="$1"
  local install_hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing CLI: $cmd ($install_hint)"
    missing=1
  fi
}

check_url() {
  local url="$1"
  if ! curl -fsS --max-time 8 "$url" >/dev/null 2>&1; then
    echo "Network check failed: $url"
    missing=1
  fi
}

check_env RAILWAY_TOKEN
check_env VERCEL_TOKEN

check_cmd railway "npm i -g @railway/cli"
check_cmd vercel "npm i -g vercel"

check_url https://api.vercel.com
check_url https://backboard.railway.app
check_url https://github.com

if [ "$missing" -ne 0 ]; then
  cat <<MSG

Cloud deploy preflight failed.
Optional but recommended environment variables:
- RAILWAY_PROJECT_ID
- RAILWAY_SERVICE_ID
- VERCEL_ORG_ID
- VERCEL_PROJECT_ID
MSG
  exit 1
fi

echo "Cloud deploy preflight passed."
