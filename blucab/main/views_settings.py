from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from .models import UserSettings, MovieUserList, Movie
from .forms import (
    UpdateUserSettings,
    UpdateMovieUserList,
    UpdateMovie,
)


@login_required
def user_settings(request):
    user = request.user
    user_settings_model = UserSettings.objects.get(user=user)

    if request.method == "POST":
        form = UpdateUserSettings(request.POST, instance=user_settings_model)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                user_settings_model.__dict__[field] = value
            user_settings_model.save()
    else:
        form = UpdateUserSettings(instance=user_settings_model)

    return render(
        request,
        "main/settings_user.html",
        {
            "form": form,
            "usersettings": user_settings_model,
        },
    )


@login_required
def movie_settings(request, movie_id):
    user = request.user

    is_moderator = user.groups.filter(name="Moderator-Movie").exists()

    if not (user.is_superuser or is_moderator):
        return render(request, "error/403.html", status=403)

    try:
        movie_model = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return render(request, "error/404.html", status=404)

    if request.method == "POST":
        form = UpdateMovie(request.POST, instance=movie_model)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                movie_model.__dict__[field] = value
            movie_model.save()

        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("view")
    else:
        form = UpdateMovie(instance=movie_model)

    next_url = request.GET.get("next", "")

    return render(
        request,
        "main/settings_movie.html",
        {"form": form, "movie": movie_model, "next_url": next_url},
    )


@login_required
def user_movie_settings(request, movie_id):
    user = request.user

    try:
        user_movie_model = MovieUserList.objects.get(user=user, movie=movie_id)
    except MovieUserList.DoesNotExist:
        return render(request, "error/404.html", status=404)

    if request.method == "POST" and "delete" in request.POST:
        user_movie_model.delete()
        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("view")

    if request.method == "POST":
        form = UpdateMovieUserList(request.POST, instance=user_movie_model, user=user)

        if form.is_valid():
            for field, value in form.cleaned_data.items():
                user_movie_model.__dict__[field] = value
            user_movie_model.save()

            next_url = request.POST.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("view")
    else:
        form = UpdateMovieUserList(instance=user_movie_model, user=user)

    next_url = request.GET.get("next", "")

    return render(
        request,
        "main/settings_user_movie.html",
        {"form": form, "movie": user_movie_model.movie, "next_url": next_url},
    )
