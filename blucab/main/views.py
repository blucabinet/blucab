from django.shortcuts import render
from .models import UserSettings, MovieUserList, User
from .forms import UpdateUserSettings

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


def index(response, uname):
    user_id_query = User.objects.filter(username=uname)
    if len(user_id_query) != 1:
        return render(response, "error/403_user_not_public.html", {})

    user_id = user_id_query[0].id
    view_is_public = UserSettings.objects.all().filter(user=user_id)[0].view_is_public

    if not view_is_public:
        return render(response, "error/403_user_not_public.html", {})

    ls = MovieUserList.objects.all().filter(user=user_id)

    for movie in ls:
        print(movie.movie.title_clean)

    return render(response, "main/view.html", {})


def csv_import(response):
    # Import dataset from Flick-Rack
    test = None
    user = response.user
    username = user.username

    if user.is_authenticated:

        ch = handler()

        file = username + ".csv"
        ch.csv_importer(filename=file, user=user)

        ch.content_update()
    else:
        pass

    return render(response, "main/csv_import.html", {"data": test})


def home(response):
    return render(response, "main/home.html", {})


def add_movie(response):
    user = response.user

    if user.is_authenticated:
        return render(response, "main/add_movie.html", {})
    else:
        return render(response, "main/add_movie.html")
    
def view(response):
    user = response.user

    if user.is_authenticated:
        usersettings = user.user_profile
        return render(response, "main/view.html", {"usersettings": usersettings})
    else:
        return render(response, "main/view.html")


def settings(response):
    user = response.user

    if not user.is_authenticated:
        return render(response, "error/403.html", {})

    user_settings = UserSettings.objects.get(user=user)

    if response.method == "POST":
        form = UpdateUserSettings(response.POST)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                print(field)
                user_settings.__dict__[field] = value
            user_settings.save()
    else:
        form = UpdateUserSettings(instance=user_settings)

    return render(response, "main/settings.html", {"form": form})
