from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .forms import RegisterForm, ChangePasswordForm

from environs import Env
env = Env()
env.read_env()

ALLOW_REGISTRATION = env.bool("BLUCAB_ALLOW_REGISTER", False)


def register(request):
    if not ALLOW_REGISTRATION:
        return render(request, "error/403.html", {})

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            login(request, new_user)

            return redirect("/user/settings")
    else:
        form = RegisterForm()

    return render(request, "register/register.html", {"form": form})


def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("/user/change_password/done")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ChangePasswordForm(request.user)

    return render(request, "register/change_password.html", {"form": form})


def change_password_done(request):
    return render(request, "register/change_password_done.html", {})


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


def delete_user_done(request):
    return render(request, "register/delete_user_done.html", {})
