#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Python syntax check"
python3 -m compileall "$ROOT_DIR/backend" "$ROOT_DIR/training"

echo "==> Validate Vercel config"
python3 -m json.tool "$ROOT_DIR/vercel.json" >/dev/null

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  echo "==> Validate Docker Compose config"
  (cd "$ROOT_DIR" && docker compose config >/dev/null)
else
  echo "==> Skip Docker Compose config validation; docker compose is not available"
fi

echo "==> Frontend install, lint, and production build"
(cd "$ROOT_DIR/frontend" && npm ci && npm run lint && npm run build)

echo "==> Verification complete"
