# Deployment Guide

This reference deployment uses systemd-managed services on a single host. Adapt the same concepts for containers or orchestration platforms (Docker, Kubernetes, Nomad, etc.).

## Components
- **API** (`backend.main:app`) – served by Uvicorn/Gunicorn behind a reverse proxy.
- **Celery worker** – runs `backend.celery_app.celery_app` for OCR/LLM/PDF workloads.
- **Redis** – Celery broker/result backend.
- **PostgreSQL** – primary database (SQLite suitable only for local dev).
- **Shared volume** – `/opt/sjwg-ai-reporter/uploads` must be persistent/shared between API and worker.

## Environment & Secrets
Store secrets (DB url, JWT keys, GROQ key, etc.) in `/opt/sjwg-ai-reporter/.env` or, preferably, inject them with a secrets manager. Rotate keys periodically—refresh tokens pick up new secrets as soon as the client re-authenticates.

## Systemd Units
### API service (`/etc/systemd/system/sjwg-api.service`)
```
[Unit]
Description=SJWG AI Reporter API
After=network.target postgresql.service redis.service

[Service]
Type=simple
WorkingDirectory=/opt/sjwg-ai-reporter
EnvironmentFile=/opt/sjwg-ai-reporter/.env
ExecStart=/opt/sjwg-ai-reporter/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000 --workers 4
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Celery worker (`/etc/systemd/system/sjwg-worker.service`)
```
[Unit]
Description=SJWG AI Reporter Celery Worker
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
WorkingDirectory=/opt/sjwg-ai-reporter
EnvironmentFile=/opt/sjwg-ai-reporter/.env
ExecStart=/opt/sjwg-ai-reporter/venv/bin/celery -A backend.celery_app.celery_app worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

Reload systemd and enable the services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sjwg-api.service sjwg-worker.service
```

## Reverse Proxy
Terminate TLS at Nginx/Traefik/Caddy and proxy `/api` to `localhost:8000`. Serve the `frontend/dist` build via the same proxy or a CDN. Example Nginx location block:
```
location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Containers (Optional)
If you containerize the stack, create:
- `api` image running `uvicorn backend.main:app`
- `worker` image running `celery -A backend.celery_app.celery_app worker`
- `nginx` (or similar) that serves the built frontend and proxies `/api`
- Named volumes for `/uploads` and Alembic migrations.

## Backups & Monitoring
- Use `scripts/backup.sh` to run `pg_dump` on a schedule.
- Ship logs (stdout/systemd journal) to your observability stack.
- Monitor Celery queue depth and worker health to catch OCR/LLM bottlenecks early.
