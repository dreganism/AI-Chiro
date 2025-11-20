import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from backend.api.middleware import SimpleRateLimiterMiddleware
from backend.api.routes import router
from backend.config import settings

app = FastAPI(
    title="SJWG AI Reporter",
    version="1.0.0",
    description="Medical/Legal AI Report Generator"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SimpleRateLimiterMiddleware,
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)

app.include_router(router, prefix="/api")
app.mount("/uploads", StaticFiles(directory="/opt/sjwg-ai-reporter/uploads"), name="uploads")

@app.get("/")
def root():
    return {"message": "SJWG AI Reporter backend is running!"}

@app.get("/docs", include_in_schema=False)
def swagger_ui():
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="SJWG AI Reporter")

@app.get("/health")
def health():
    return {"status": "ok"}
