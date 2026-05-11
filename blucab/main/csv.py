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

import os


@login_required
def csv_import(request):
    user = request.user

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
        uploaded_file_url = filestorage.url(filename)

        ch = handler()
        success = ch.csv_importer(filename=filename, user=user)

        if success:
            messages.success(request, _("CSV import successfully completed."))
            pass
            # Add to a scheduler TBD
            # ch.content_update()
        else:
            messages.error(request, _("Error. Unknown CSV format."))

        os.remove(os.path.join(settings.BASE_DIR, "import", filename))

        return render(
            request,
            "main/csv_import.html",
        )

    return render(request, "main/csv_import.html", {})


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
