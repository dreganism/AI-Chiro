import os

from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

celery_app = Celery("worker", broker=REDIS_URL, backend=RESULT_BACKEND)
celery_app.conf.task_routes = {"backend.tasks.*": {"queue": "tasks"}}
celery_app.autodiscover_tasks(["backend.tasks"])
