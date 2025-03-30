from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import RegisterForm, ChangePasswordForm

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


def change_password(response):
    if response.method == "POST":
        form = ChangePasswordForm(response.user, response.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(response, user)
            messages.success(response, "Your password was successfully updated!")
            return redirect("/user/change_password/done")
        else:
            messages.error(response, "Please correct the error below.")
    else:
        form = ChangePasswordForm(response.user)

    return render(response, "register/change_password.html", {"form": form})


def change_password_done(response):
    return render(response, "register/change_password_done.html", {})
