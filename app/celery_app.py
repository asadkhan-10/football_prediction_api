# app/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "football_api",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)