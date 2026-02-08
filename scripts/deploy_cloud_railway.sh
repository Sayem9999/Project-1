#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: '$cmd' is required but not installed." >&2
    exit 1
  fi
}

normalize_optional_var() {
  local value="${1:-}"
  if [[ -z "$value" || "$value" == "..." ]]; then
    echo ""
  else
    echo "$value"
  fi
}

require_cmd railway

RAILWAY_TOKEN_VALUE="${RAILWAY_TOKEN:-}"
if [[ -z "$RAILWAY_TOKEN_VALUE" || "$RAILWAY_TOKEN_VALUE" == "..." ]]; then
  echo "Error: RAILWAY_TOKEN must be set to a valid Railway API token." >&2
  exit 1
fi

BACKEND_SERVICE_ID="$(normalize_optional_var "${RAILWAY_SERVICE_ID:-}")"
FRONTEND_SERVICE_ID="$(normalize_optional_var "${RAILWAY_FRONTEND_SERVICE_ID:-}")"

# Avoid relying on globally exported placeholders.
export RAILWAY_TOKEN="$RAILWAY_TOKEN_VALUE"

run_railway_up() {
  local dir="$1"
  local label="$2"
  local service_id="$3"

  if [[ ! -d "$dir" ]]; then
    echo "Error: expected directory '$dir' for $label service was not found." >&2
    exit 1
  fi

  local args=(up --ci)
  if [[ -n "$service_id" ]]; then
    args+=(--service "$service_id")
  fi

  echo "Deploying $label from $dir"
  (
    cd "$dir"
    railway "${args[@]}"
  )
}

run_railway_up "$BACKEND_DIR" "backend" "$BACKEND_SERVICE_ID"
run_railway_up "$FRONTEND_DIR" "frontend" "$FRONTEND_SERVICE_ID"

echo "Railway deployment commands completed."
