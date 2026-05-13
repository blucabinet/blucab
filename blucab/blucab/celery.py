import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blucab.settings")

app = Celery("blucab")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "cleanup-inactive-users-every-hour": {
        "task": "register.tasks.delete_inactive_users",
        "schedule": crontab(minute=0),
    },
}
