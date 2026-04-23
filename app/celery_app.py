# app/celery_app.py
from celery import Celery
from celery.schedules import crontab
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

celery_app.conf.beat_schedule = {
    "sync-fixtures-daily": {
        "task": "app.tasks.sync_fixtures_task",
        "schedule": crontab(hour=3, minute=0),  # runs at 3am every day
    },
    "sync-teams-weekly": {
        "task": "app.tasks.sync_teams_task",
        "schedule": crontab(hour=3, minute=0, day_of_week=1),  # runs Monday 3am
    },
}