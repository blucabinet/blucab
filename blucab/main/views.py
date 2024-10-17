from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, UserSettings, MovieUserList, User
from .forms import CreateNewList

from contenthandler.content_handler import handler

import csv
import os
import requests

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

    ch = handler()

    file = username + ".csv"
    ch.csv_importer(filename=file, user=user)

    return render(response, "main/csv_import.html", {"data": test})


def home(response):
    return render(response, "main/home.html", {})


def view(response):
    user = response.user

    if user.is_authenticated:
        usersettings = user.user_profile
        return render(response, "main/view.html", {"usersettings": usersettings})
    else:
        return render(response, "main/view.html")
