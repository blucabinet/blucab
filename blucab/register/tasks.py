# users/tasks.py (oder in der entsprechenden App)
from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


@shared_task
def delete_inactive_users():
    time_threshold = timezone.now() - timedelta(hours=24)

    inactive_users = User.objects.filter(
        is_active=False, date_joined__lt=time_threshold
    )

    count = inactive_users.count()
    inactive_users.delete()

    return f"{count} inactive Accounts deleted."
