from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item
from .forms import CreateNewList

import csv
import os
import requests
from django.conf import settings

# Create your views here.
url = "https://m.media-amazon.com/images/I/51DUcBqDTcL._SX300_SY300_QL70_ML2_.jpg"
picture = requests.get(url)
picture_name = "apollo" + ".jpg"
file_path = os.path.join(settings.BASE_DIR, "main", "static", "main", picture_name)

def index(response, id):
    ls = ToDoList.objects.get(id=id)

    if ls in response.user.todolist.all():

        if response.method == "POST":
            print(response.POST)
            if response.POST.get("save"):
                for item in ls.item_set.all():
                    if response.POST.get("c" + str(item.id)) == "clicked":
                        item.complete = True
                    else:
                        item.complete = False

                    item.save()

            elif response.POST.get("newItem"):
                txt = response.POST.get("new")

                # Validity check
                if len(txt) > 2:
                    ls.item_set.create(text=txt, complete=False)
                else:
                    print("invalid input")

        return render(response, "main/list.html", {"ls": ls})
    return render(response, "main/view.html", {})

def csv_import(response):
    test = None
    
    if not os.path.exists(file_path):
        open(file_path, "wb").write(picture.content)
        print(f"File {picture_name} downloaded")

    with open(os.path.join(settings.BASE_DIR, "import/floyer_movies.csv")) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for row in reader:
           #print(row[3])
            test = row[3]

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
    return render(response, "main/view.html", {"path": picture_name})
