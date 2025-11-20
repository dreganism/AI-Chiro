# SJWG AI Reporter

SJWG AI Reporter ingests medical images and documents, extracts text with OCR, and summarizes it into a structured report using an LLM. The project now pairs a FastAPI backend with a Vite/React frontend and a Celery worker dedicated to long-running OCR/LLM/PDF work.

## Stack Overview
- **Backend**: FastAPI, SQLAlchemy, Alembic, Celery, PostgreSQL (SQLite used for local/dev/testing).
- **AI/OCR**: Tesseract via `pytesseract`, `pdf2image`, WeasyPrint for PDF output, Groq Llama models for summaries (pluggable).
- **Frontend**: Vite + React 18 + plain CSS (ready for Tailwind or shadcn if you prefer).
- **Workers**: Celery (Redis broker) executes OCR/LLM/PDF generation so the API stays responsive.

## Prerequisites
1. Python 3.11+
2. Node 18+ (optional for future frontend build steps)
3. PostgreSQL 14+ (or SQLite for quick starts)
4. Redis (for Celery broker/result backend)
5. System packages:
   - `tesseract-ocr`
   - `poppler-utils` (needed by `pdf2image`)
   - `libpango`, `libcairo`, and other WeasyPrint deps (install via your package manager)

## Getting Started
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # create from scratch if needed
```

Populate `.env` with the following keys:

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | e.g. `postgresql://user:pass@localhost:5432/sjwg_reporter` or `sqlite:///./app.db` |
| `SECRET_KEY` | FastAPI session/CSRF secret |
| `JWT_SECRET_KEY` | Secret used to sign auth tokens |
| `JWT_ALGORITHM` | Defaults to `HS256` |
| `GROQ_API_KEY` | API key used by the report generator |
| `REDIS_URL` | Celery broker (defaults to `redis://localhost:6379/0`) |
| `CELERY_RESULT_BACKEND` | Optional explicit backend (defaults to Redis broker) |
| `CORS_ALLOW_ORIGINS` | Comma-separated list of web origins allowed by the API |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token lifetime |
| `RATE_LIMIT_REQUESTS/RATE_LIMIT_WINDOW_SECONDS` | Basic rate limiter knobs |
| `PASSWORD_MIN_LENGTH/PASSWORD_REQUIRE_SPECIAL` | Password strength policy |
| `OPENAI_API_KEY` | Reserved for future integrations |

Apply migrations (or rely on SQLAlchemy auto-create for SQLite):
```bash
alembic upgrade head
```

Run the backend API:
```bash
uvicorn backend.main:app --reload --port 8000
```

Run the Celery worker in another terminal so uploads are processed:
```bash
celery -A backend.celery_app.celery_app worker --loglevel=info
```

### Frontend (Vite)
```bash
cd frontend
npm install
npm run dev   # proxies to http://localhost:8000/api by default
npm run build # for production bundles in frontend/dist
```

Set `VITE_API_BASE` (dev/build) if the API is not available on the same origin.

### Security defaults
- Passwords must meet the policy defined by `PASSWORD_MIN_LENGTH`/`PASSWORD_REQUIRE_SPECIAL`.
- JWT auth now issues access + refresh tokens (`/api/auth/refresh`, `/api/auth/logout`).
- Rate limiting middleware protects every request using the configurable window/limit knobs.
- CORS origins are explicit instead of `*`; set `CORS_ALLOW_ORIGINS` to the web clients you trust.

## Running Tests
```bash
pytest
```
The suite spins up an isolated SQLite database and exercises the core FastAPI flows plus utility modules.

## Deployment Notes
- Scripts under `scripts/` document how to run database migrations, back up the database, set up SSL, and restart services. Pair them with the systemd sample units in `docs/deployment.md` or adapt them for containers.
- Provision Redis, PostgreSQL, and a persistent `/uploads` volume in production. Run at least two services: the API (gunicorn/uvicorn) and the Celery worker.
- Provide secrets through your orchestrator/secret manager and rotate them regularly (refresh tokens inherit the updated signing key immediately).

See `docs/API.md` for the REST contract and `docs/deployment.md` for infra examples.
