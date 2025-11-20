# API Reference

Base URL defaults to `/api`. Authenticate with the `Authorization: Bearer <token>` header unless otherwise noted.

## Auth
### POST /api/auth/register
Creates a user (password must satisfy policy).
- Body (form-encoded): `email`, `password`
- 200 Response:
```json
{"message":"User created successfully","email":"user@example.com"}
```

### POST /api/auth/login
Authenticates and returns a JWT.
- Body (form-encoded): `email`, `password`
- 200 Response:
```json
{"access_token":"<jwt>","refresh_token":"<jwt>","token_type":"bearer"}
```

### POST /api/auth/refresh
Issues a new access token when given a valid refresh token.
- Body (form-encoded): `refresh_token`
- 200 Response:
```json
{"access_token":"<jwt>","token_type":"bearer"}
```

### POST /api/auth/logout
Stateless logout helper. Clients should delete their stored tokens.
- 200 Response:
```json
{"message":"Logged out. Please discard tokens on the client."}
```

## Reports
### GET /api/reports
Returns the authenticated user’s reports ordered by `created_at` desc.
- 200 Response:
```json
[
  {
    "id": 1,
    "title": "scan.pdf",
    "status": "completed",
    "created_at": "2025-01-05T18:23:00",
    "pdf_report": "/uploads/reports/report_1.pdf"
  }
]
```

### GET /api/reports/{id}
Fetches a single report plus summary preview.
- 200 Response:
```json
{
  "id": 1,
  "title": "scan.pdf",
  "status": "completed",
  "created_at": "2025-01-05T18:23:00",
  "download_pdf": "/uploads/reports/report_1.pdf",
  "preview": "Short excerpt of the AI summary..."
}
```

### DELETE /api/reports/{id}
Removes a report owned by the authenticated user. Deletes the generated PDF if present.
- 204 Response: empty body

## Upload
### POST /api/upload
Uploads a PDF/JPEG/PNG. The server saves the file, enqueues OCR + LLM work through Celery, and responds immediately with a report ID.
- Headers: `Authorization: Bearer <token>`
- Body: multipart `file`
- 202 Response:
```json
{
  "report_id": 2,
  "status": "processing",
  "message": "File uploaded. OCR + AI report in progress...",
  "check_status": "/api/reports/2"
}
```

## Health
### GET /health
Returns `{ "status": "ok" }` and is unauthenticated.
