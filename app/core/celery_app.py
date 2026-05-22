from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "fiscalbot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.alertas", "app.tasks.importacao"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    beat_schedule={
        "checar-vencimentos-diario": {
            "task": "app.tasks.alertas.checar_vencimentos",
            "schedule": crontab(hour=7, minute=0),
        },
        "checar-reajustes-diario": {
            "task": "app.tasks.alertas.checar_reajustes",
            "schedule": crontab(hour=7, minute=5),
        },
    },
)
