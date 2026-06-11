#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export PREFECT_API_URL="${PREFECT_API_URL:-http://127.0.0.1:4200/api}"

if ! prefect work-pool inspect default-process-pool >/dev/null 2>&1; then
  prefect work-pool create --type process default-process-pool
fi

prefect deploy --all
