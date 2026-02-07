#!/usr/bin/env bash
set -euo pipefail

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "VERCEL_TOKEN is required for non-interactive deploy"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v vercel >/dev/null 2>&1; then
  VERCEL_CMD=(vercel)
else
  VERCEL_CMD=(npx vercel)
fi

SCOPE_ARGS=()
if [ -n "${VERCEL_ORG_ID:-}" ]; then
  SCOPE_ARGS+=("--scope" "$VERCEL_ORG_ID")
fi

${VERCEL_CMD[@]} pull --yes --environment=production --token "$VERCEL_TOKEN" "${SCOPE_ARGS[@]}"
${VERCEL_CMD[@]} deploy --prod --yes --token "$VERCEL_TOKEN" "${SCOPE_ARGS[@]}"
