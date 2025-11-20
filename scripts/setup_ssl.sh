#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${DOMAIN:-example.com}
EMAIL=${EMAIL:-admin@example.com}

if ! command -v certbot >/dev/null; then
  echo "Please install certbot before running this script" >&2
  exit 1
fi

sudo certbot certonly --standalone -d "$DOMAIN" -m "$EMAIL" --agree-tos --non-interactive

echo "Certificates stored under /etc/letsencrypt/live/$DOMAIN"
