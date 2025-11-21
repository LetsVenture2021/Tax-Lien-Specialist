"""Celery application instance accessible for background job execution."""

from celery import Celery

from app.core.config import settings


celery_app = Celery("tax_lien_strategist")
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.timezone = "UTC"


@celery_app.task(name="app.jobs.health.ping")
def ping() -> str:
    """Simple ping task to verify worker wiring."""
    return "pong"
