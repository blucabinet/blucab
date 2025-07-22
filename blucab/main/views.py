from django.shortcuts import render
from django.conf import settings
from .models import UserSettings, MovieUserList, User
from .forms import UpdateUserSettings
from django.core.files.storage import FileSystemStorage

import os

from contenthandler.content_handler import handler


# Create your views here.
def handler_400(request, exception):
    return render(request, "error/400.html", status=400)


def handler_403(request, exception):
    return render(request, "error/403.html", status=403)


def handler_404(request, exception):
    return render(request, "error/404.html", status=404)


def handler_500(request):
    return render(request, "error/500.html", status=500)


def legal(request):
    return render(request, "legal/legal.html", {})


def privacy(request):
    return render(request, "legal/privacy.html", {})


def cab_uname(request, uname):
    user = request.user
    user_id_query = User.objects.filter(username=uname)
    
    if len(user_id_query) != 1:
        return render(request, "error/403_user_not_public.html", {})

    user_id = user_id_query[0].id
    usersettings = UserSettings.objects.all().filter(user=user_id)[0]
    view_is_public = usersettings.view_is_public

    if not view_is_public:
        return render(request, "error/403_user_not_public.html", {})

    movieuserlist = MovieUserList.objects.all().filter(user=user_id)

    if user.is_authenticated:
        show_view_title = user.user_profile.show_view_title
    else:
        show_view_title = True

    return render(
        request,
        "main/view.html",
        {"movieuserlist": movieuserlist, "usersettings": usersettings, "is_user_view": False, "show_view_title": show_view_title},
    )


def csv_import(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", {})
    
    if request.method == "POST":
        file = request.FILES.get("myfile", None)

        if not file:
            return render(
                request,
                "main/csv_import.html",
                {"message": "Please select a file to upload."},
            )

        myfile = request.FILES["myfile"]
        file_path = os.path.join(settings.BASE_DIR, "import")

        filestorage = FileSystemStorage(location=str(file_path))
        filename = filestorage.save(myfile.name, myfile)
        uploaded_file_url = filestorage.url(filename)

        ch = handler()
        ch.csv_importer(filename=filename, user=user)
        ch.content_update()

        os.remove(os.path.join(settings.BASE_DIR, "import", filename))

        return render(
            request,
            "main/csv_import.html",
            {"uploaded_file_url": uploaded_file_url},
        )

    return render(request, "main/csv_import.html", {})


def home(request):
    return render(request, "main/home.html", {})


def add_movie(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", {})
        
    return render(request, "main/add_movie.html", {})



def view(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", {})

    usersettings = user.user_profile
    movieuserlist = MovieUserList.objects.all().filter(user=user)
    return render(
        request,
        "main/view.html",
        {"movieuserlist": movieuserlist, "usersettings": usersettings, "is_user_view": True},
    )


def user_settings(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", {})

    user_settings_model = UserSettings.objects.get(user=user)

    if request.method == "POST":
        form = UpdateUserSettings(request.POST)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                print(field)
                user_settings_model.__dict__[field] = value
            user_settings_model.save()
    else:
        form = UpdateUserSettings(instance=user_settings_model)

    return render(request, "main/settings.html", {"form": form})
