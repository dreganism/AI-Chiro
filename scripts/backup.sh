#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=${BACKUP_DIR:-/opt/sjwg-ai-reporter/backups}
mkdir -p "$BACKUP_DIR"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL not set" >&2
  exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
pg_dump "$DATABASE_URL" > "$BACKUP_DIR/db-$TIMESTAMP.sql"
