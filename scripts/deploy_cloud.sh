#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT_DIR/scripts/preflight_cloud.sh"
"$ROOT_DIR/scripts/deploy_railway.sh"
"$ROOT_DIR/scripts/deploy_vercel.sh"

echo "Cloud deployment commands executed for Railway and Vercel."
