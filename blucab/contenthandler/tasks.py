from celery import shared_task
from contenthandler.content_handler import handler
from contenthandler.models import FailedAddMovie


@shared_task(rate_limit="10/m")
def task_add_new_movie(ean: str) -> None:
    ch = handler()
    success, exists = ch.add_new_movie(ean)

    if success and not exists:
        print(f"Successfully added new movie with EAN {ean}")

    if not success and exists:
        print(f"Movie with EAN {ean} already exists in database.")

    if not success and not exists:
        FailedAddMovie.objects.create(ean=ean)
        print(f"Failed to add movie with EAN {ean}. Saving to FailedAddMovie.")

    return
