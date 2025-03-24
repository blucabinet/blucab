from django.shortcuts import render, redirect
from .forms import RegisterForm

from environs import Env
from dotenv import load_dotenv
from dotenv import find_dotenv

env = Env()
load_dotenv(find_dotenv())

ALLOW_REGISTRATION = env.bool("BLUCAB_ALLOW_REGISTER", False)


def register(response):
    if not ALLOW_REGISTRATION:
        return render(response, "error/403.html", {})

    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()

        return redirect("/")
    else:
        form = RegisterForm()

    return render(response, "register/register.html", {"form": form})
