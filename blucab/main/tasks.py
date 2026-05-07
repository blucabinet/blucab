from celery import shared_task
from contenthandler.content_handler import handler


@shared_task(rate_limit="10/m")
def fetch_movie_data_task(ean: str):
    ch = handler()
    success = ch.add_new_movie(ean)
    if success:
        print(f"Successfully added movie with EAN {ean}")
    else:
        print(f"Failed to add movie with EAN {ean}")
    return success
