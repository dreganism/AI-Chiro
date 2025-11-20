#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=${ENV_FILE:-/opt/sjwg-ai-reporter/.env}
APP_DIR=${APP_DIR:-/opt/sjwg-ai-reporter}

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing env file at $ENV_FILE" >&2
  exit 1
fi

cd "$APP_DIR"
source "$ENV_FILE"

. venv/bin/activate
alembic upgrade head

# Reload gunicorn/uvicorn service managed by systemd
if command -v systemctl >/dev/null; then
  sudo systemctl restart sjwg-api.service
  sudo systemctl restart sjwg-worker.service || true
else
  echo "systemctl not available; start the server manually with uvicorn backend.main:app" >&2
fi
