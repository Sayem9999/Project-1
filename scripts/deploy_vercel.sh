#!/usr/bin/env bash
set -euo pipefail

if ! command -v vercel >/dev/null 2>&1; then
  echo "Vercel CLI not found. Install with: npm i -g vercel"
  exit 1
fi

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "VERCEL_TOKEN is required for non-interactive deploy"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/frontend"

SCOPE_ARGS=()
if [ -n "${VERCEL_ORG_ID:-}" ]; then
  SCOPE_ARGS+=("--scope" "$VERCEL_ORG_ID")
fi

vercel pull --yes --environment=production --token "$VERCEL_TOKEN" "${SCOPE_ARGS[@]}"
vercel deploy --prod --yes --token "$VERCEL_TOKEN" "${SCOPE_ARGS[@]}"
