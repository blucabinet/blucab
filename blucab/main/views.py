from django.shortcuts import render, redirect
from django.conf import settings
from .models import UserSettings, MovieUserList, User, Movie
from .forms import UpdateUserSettings, UpdateMovieUserList, UpdateMovie
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse

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
        return render(request, "error/403_user_not_public.html", status=403)

    user_id = user_id_query[0].id
    usersettings = UserSettings.objects.filter(user=user_id)[0]
    view_is_public = usersettings.view_is_public

    if not view_is_public:
        return render(request, "error/403_user_not_public.html", status=403)

    movieuserlist = MovieUserList.objects.filter(user=user_id)
    count_dvd = MovieUserList.objects.filter(user=user, movie__format="DVD").count()
    count_bd = MovieUserList.objects.filter(user=user, movie__format="Blu-Ray").count()
    count_total = movieuserlist.count()

    if user.is_authenticated:
        show_view_title = user.user_profile.show_view_title
        show_card_body = show_view_title
    else:
        show_view_title = True
        show_card_body = True

    return render(
        request,
        "main/view.html",
        {
            "movieuserlist": movieuserlist,
            "usersettings": usersettings,
            "is_user_view": False,
            "show_view_title": show_view_title,
            "show_card_body": show_card_body,
            "count_dvd": count_dvd,
            "count_bd": count_bd,
            "count_total": count_total,
        },
    )


def view(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", status=403)

    usersettings = user.user_profile
    movieuserlist = MovieUserList.objects.filter(user=user)
    count_dvd = MovieUserList.objects.filter(user=user, movie__format="DVD").count()
    count_bd = MovieUserList.objects.filter(user=user, movie__format="Blu-Ray").count()
    count_total = movieuserlist.count()

    return render(
        request,
        "main/view.html",
        {
            "movieuserlist": movieuserlist,
            "usersettings": usersettings,
            "is_user_view": True,
            "show_card_body": True,
            "count_dvd": count_dvd,
            "count_bd": count_bd,
            "count_total": count_total,
        },
    )


def csv_import(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", status=403)

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
        success = ch.csv_importer(filename=filename, user=user)

        if success:
            ch.content_update()
        else:
            uploaded_file_url = "Error. Unknown CSV format."

        os.remove(os.path.join(settings.BASE_DIR, "import", filename))
        
        return render(
            request,
            "main/csv_import.html",
            {"uploaded_file_url": uploaded_file_url},
        )

    return render(request, "main/csv_import.html", {})


def csv_export(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", status=403)

    ch = handler()
    data = ch.csv_exporter(user=user)

    return HttpResponse(data, content_type="text/csv")


def home(request):
    return render(request, "main/home.html", {})


def add_movie(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", status=403)

    return render(request, "main/add_movie.html", {})


def user_settings(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", status=403)

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

    return render(request, "main/settings_user.html", {"form": form})


def movie_settings(request, movie_id):
    user = request.user

    if not user.is_superuser:
        return render(request, "error/403.html", status=403)

    try:
        movie_model = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return render(request, "error/404.html", status=404)

    if request.method == "POST":
        form = UpdateMovie(request.POST)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                print(field)
                movie_model.__dict__[field] = value
            movie_model.save()
            return redirect("/view")
    else:
        form = UpdateMovie(instance=movie_model)

    return render(
        request, "main/settings_movie.html", {"form": form, "movie": movie_model}
    )


def user_movie_settings(request, movie_id):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", status=403)

    try:
        user_movie_model = MovieUserList.objects.get(user=user, movie=movie_id)
    except MovieUserList.DoesNotExist:
        return render(request, "error/404.html", status=404)

    if request.method == "POST":
        form = UpdateMovieUserList(request.POST)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                print(field)
                user_movie_model.__dict__[field] = value
            user_movie_model.save()
            return redirect("/view")
    else:
        form = UpdateMovieUserList(instance=user_movie_model)

    return render(
        request,
        "main/settings_user_movie.html",
        {"form": form, "movie": user_movie_model.movie},
    )


