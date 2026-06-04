from django.db.models import Q
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import UserSettings
from contenthandler.content_handler import handler
from contenthandler.tasks import task_import_csv

import os


@login_required
def csv_import(request):
    user = request.user
    context = {}

    if request.method == "POST":
        file = request.FILES.get("myfile", None)

        if not file:
            return render(
                request,
                "main/csv_import.html",
                {"message": _("Please select a file to upload.")},
            )

        myfile = request.FILES["myfile"]
        file_path = os.path.join(settings.BASE_DIR, "import")

        filestorage = FileSystemStorage(location=str(file_path))
        filename = filestorage.save(myfile.name, myfile)

        task = task_import_csv.delay(filename=filename, user_id=user.id)
        messages.info(
            request, _("CSV import started in the background. Please wait...")
        )

        context["task_id"] = task.id

        return render(request, "main/csv_import.html", context)

    return render(request, "main/csv_import.html", context)


@login_required
def csv_export(request):
    user = request.user
    user_settings_model = UserSettings.objects.get(user=user)

    ch = handler()
    data = ch.csv_exporter(user=user)

    user_settings_model.last_export = timezone.now()
    user_settings_model.save()

    response = HttpResponse(data, content_type="text/csv")

    date_str = timezone.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_{user.username}_blucab-movies.csv"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


@login_required
def content_update(request):
    ch = handler()
    ch.content_update()
    return render(request, "main/home.html", {})
