from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
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


def delete_user(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", {})

    if request.method == "GET":
        return render(request, "register/delete_user_confirm.html", {})
    elif request.method == "POST":
        user_object = User.objects.get(username=user)
        user_object.delete()
        update_session_auth_hash(request, user)
        return redirect("/user/delete/done")


def delete_user_done(response):
    return render(response, "register/delete_user_done.html", {})
