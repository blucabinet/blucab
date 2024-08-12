from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, UserSettings, MovieUserList, User
from .forms import CreateNewList

from .content_handler import handler

import csv
import os
import requests

# Create your views here.
url = "https://m.media-amazon.com/images/I/51DUcBqDTcL._SX300_SY300_QL70_ML2_.jpg"


def handler_400(request, exception):
    return render(request, "error/400.html", status=400)


def handler_403(request, exception):
    return render(request, "error/403.html", status=403)


def handler_404(request, exception):
    return render(request, "error/404.html", status=404)


def handler_500(request):
    return render(request, "error/500.html", status=500)


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

    # if ls in response.user.todolist.all():
    #
    #    if response.method == "POST":
    #        print(response.POST)
    #        if response.POST.get("save"):
    #            for item in ls.item_set.all():
    #                if response.POST.get("c" + str(item.id)) == "clicked":
    #                    item.complete = True
    #                else:
    #                    item.complete = False
    #
    #                item.save()
    #
    #        elif response.POST.get("newItem"):
    #            txt = response.POST.get("new")
    #
    #            # Validity check
    #            if len(txt) > 2:
    #                ls.item_set.create(text=txt, complete=False)
    #            else:
    #                print("invalid input")
    #
    #    return render(response, "main/list.html", {"ls": ls})
    return render(response, "main/view.html", {})


def csv_import(response):
    # Import dataset from Flick-Rack
    test = None
    user = response.user

    ch = handler()

    # ch._picture_download(url, picture_name)
    ch.csv_importer(filename="floyer_movies.csv", user=user)

    return render(response, "main/csv_import.html", {"data": test})


def home(response):
    return render(response, "main/home.html", {})


def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()
            response.user.todolist.add(t)

        return HttpResponseRedirect("/%i" % t.id)

    else:
        form = CreateNewList()

    return render(response, "main/create.html", {"form": form})


def view(response):
    user = response.user

    if user.is_authenticated:
        usersettings = user.user_profile
        return render(response, "main/view.html", {"usersettings": usersettings})
    else:
        return render(response, "main/view.html")
