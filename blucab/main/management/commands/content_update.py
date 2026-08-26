from django.core.management.base import BaseCommand
from contenthandler.tasks import task_content_update


class Command(BaseCommand):
    help = "Manually triggers the content_update Celery task."

    def handle(self, *args, **options):
        task_content_update.delay()
        self.stdout.write(
            self.style.SUCCESS("Successfully triggered content update task.")
        )
