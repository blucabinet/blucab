import os
from django.conf import settings
from django.contrib.auth import get_user_model
from celery import shared_task
from contenthandler.content_handler import handler
from contenthandler.models import FailedAddMovie

User = get_user_model()


@shared_task(rate_limit="10/m")
def task_add_new_movie(ean: str) -> bool:
    ch = handler()
    success, exists = ch.add_new_movie(ean)

    if success and not exists:
        print(f"Successfully added new movie with EAN {ean}")
        return True

    if not success and exists:
        print(f"Movie with EAN {ean} already exists in database.")
        return False

    if not success and not exists:
        FailedAddMovie.objects.create(ean=ean)
        print(f"Failed to add movie with EAN {ean}. Saving to FailedAddMovie.")
        return False

    return False


@shared_task(rate_limit="2/m")
def task_content_update() -> None:
    ch = handler()
    ch.content_update()

    return


@shared_task(rate_limit="30/m")
def task_import_csv(filename: str, user_id: int) -> bool:
    # Needs to be user_id because User objects can't be passed to Celery tasks!
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return False

    ch = handler()
    success = ch.csv_importer(filename=filename, user=user)

    # TBD Trigger content update
    if success:
        # Code to trigger content update
        pass

    file_path = os.path.join(settings.BASE_DIR, "import", filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    return success
