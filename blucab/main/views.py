from django.db.models import Q
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from .models import UserSettings, MovieUserList, User, Movie, UserCabinet
from .forms import (
    UpdateUserSettings,
    UpdateMovieUserList,
    UpdateMovie,
    CabinetAddForm,
    CabinetDeleteForm,
)

import os
from environs import Env

from contenthandler.content_handler import handler


env = Env()
env.read_env()

DEBUG = env.bool("DEBUG", False)


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
    request_user = request.user
    user_id_query = User.objects.filter(username=uname)

    if len(user_id_query) != 1:
        return render(request, "error/403_user_not_public.html", status=403)

    user = user_id_query[0].id
    usersettings = UserSettings.objects.filter(user=user)[0]
    view_is_public = usersettings.view_is_public

    if not view_is_public:
        return render(request, "error/403_user_not_public.html", status=403)

    movieuserlist = MovieUserList.objects.filter(user=user)
    count_total = movieuserlist.count()

    # Apply filters
    filter_dvd = request.GET.get("filter_dvd") == "1"
    filter_bd = request.GET.get("filter_bd") == "1"
    filter_bd_uhd = request.GET.get("filter_bd_uhd") == "1"
    filter_rented = request.GET.get("filter_rented") == "1"

    if filter_dvd or filter_bd:
        formats = []
        if filter_dvd:
            formats.append("DVD")
        if filter_bd:
            formats.append("Blu-Ray")
        movieuserlist = movieuserlist.filter(movie__format__in=formats)

    if filter_bd_uhd:
        movieuserlist = movieuserlist.filter(movie__is_bluray_uhd=True)

    if filter_rented:
        movieuserlist = movieuserlist.filter(rented=True)

    search_query = request.GET.get("search", "")
    if search_query:
        movieuserlist = movieuserlist.filter(
            Q(movie__title_clean__icontains=search_query)
        )

    sort_by = request.GET.get("sort", "")
    sort_mapping = {
        "title_asc": "movie__title_clean",
        "title_desc": "-movie__title_clean",
        "rating_desc": "-rating",
        "rating_asc": "rating",
        "date_desc": "-date_added",
        "date_asc": "date_added",
        "runtime_asc": "movie__runtime",
        "runtime_desc": "-movie__runtime",
    }

    if sort_by in sort_mapping:
        movieuserlist = movieuserlist.order_by(sort_mapping[sort_by])

    # Update counts after filtering
    count_dvd = movieuserlist.filter(movie__format="DVD").count()
    count_bd = movieuserlist.filter(movie__format="Blu-Ray").count()
    count_bd_uhd = (
        movieuserlist.filter(movie__format="Blu-Ray")
        .filter(movie__is_bluray_uhd=True)
        .count()
    )
    count_rented = movieuserlist.filter(rented=True).count()

    if request_user.is_authenticated:
        # Use the authenticated user's settings
        show_view_title = request_user.user_profile.show_view_title
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
            "uname": uname,
            "show_view_title": show_view_title,
            "show_card_body": show_card_body,
            "count_dvd": count_dvd,
            "count_bd": count_bd,
            "count_bd_uhd": count_bd_uhd,
            "count_rented": count_rented,
            "count_total": count_total,
            "search_query": search_query,
            "sort_by": sort_by,
            "filter_dvd": filter_dvd,
            "filter_bd": filter_bd,
            "filter_bd_uhd": filter_bd_uhd,
            "filter_rented": filter_rented,
        },
    )


@login_required
def view(request):
    user = request.user
    usersettings = user.user_profile

    movieuserlist = MovieUserList.objects.filter(user=user)
    count_total = movieuserlist.count()

    active_cabinet_ids = (
        movieuserlist.exclude(cabinet__isnull=True)
        .values_list("cabinet_id", flat=True)
        .distinct()
    )
    cabinets = UserCabinet.objects.filter(id__in=active_cabinet_ids)

    # Apply filters
    filter_dvd = request.GET.get("filter_dvd") == "1"
    filter_bd = request.GET.get("filter_bd") == "1"
    filter_bd_uhd = request.GET.get("filter_bd_uhd") == "1"
    filter_rented = request.GET.get("filter_rented") == "1"
    filter_viewed = request.GET.get("filter_viewed", "")
    filter_archived = request.GET.get("filter_archived", "")
    filter_is_series = request.GET.get("filter_is_series", "")
    selected_cabinet = request.GET.get("cabinet", "")
    search_query = request.GET.get("search", "")

    if filter_dvd or filter_bd:
        formats = []
        if filter_dvd:
            formats.append("DVD")
        if filter_bd:
            formats.append("Blu-Ray")
        movieuserlist = movieuserlist.filter(movie__format__in=formats)

    if filter_bd_uhd:
        movieuserlist = movieuserlist.filter(movie__is_bluray_uhd=True)

    if filter_rented:
        movieuserlist = movieuserlist.filter(rented=True)

    if filter_viewed == "1":
        movieuserlist = movieuserlist.filter(viewed=True)
    elif filter_viewed == "0":
        movieuserlist = movieuserlist.filter(viewed=False)

    if filter_archived == "1":
        movieuserlist = movieuserlist.filter(archived=True)
    elif filter_archived == "0":
        movieuserlist = movieuserlist.filter(archived=False)

    if filter_is_series == "1":
        movieuserlist = movieuserlist.filter(movie__is_series=True)
    elif filter_is_series == "0":
        movieuserlist = movieuserlist.filter(movie__is_series=False)

    if selected_cabinet:
        if selected_cabinet == "none":
            movieuserlist = movieuserlist.filter(cabinet__isnull=True)
        elif selected_cabinet:
            movieuserlist = movieuserlist.filter(cabinet_id=selected_cabinet)

    if search_query:
        movieuserlist = movieuserlist.filter(
            Q(movie__title_clean__icontains=search_query)
        )

    sort_by = request.GET.get("sort", "")
    sort_mapping = {
        "title_asc": "movie__title_clean",
        "title_desc": "-movie__title_clean",
        "rating_desc": "-rating",
        "rating_asc": "rating",
        "date_desc": "-date_added",
        "date_asc": "date_added",
        "runtime_asc": "movie__runtime",
        "runtime_desc": "-movie__runtime",
    }

    if sort_by in sort_mapping:
        movieuserlist = movieuserlist.order_by(sort_mapping[sort_by])

    # Update counts after filtering
    count_dvd = movieuserlist.filter(movie__format="DVD").count()
    count_bd = movieuserlist.filter(movie__format="Blu-Ray").count()
    count_bd_uhd = movieuserlist.filter(
        movie__format="Blu-Ray", movie__is_bluray_uhd=True
    ).count()
    count_rented = movieuserlist.filter(rented=True).count()

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
            "count_bd_uhd": count_bd_uhd,
            "count_rented": count_rented,
            "count_total": count_total,
            "search_query": search_query,
            "sort_by": sort_by,
            "filter_dvd": filter_dvd,
            "filter_bd": filter_bd,
            "filter_bd_uhd": filter_bd_uhd,
            "filter_rented": filter_rented,
            "filter_viewed": filter_viewed,
            "filter_archived": filter_archived,
            "filter_is_series": filter_is_series,
            "cabinets": cabinets,
            "selected_cabinet": selected_cabinet,
        },
    )


@login_required
def csv_import(request):
    user = request.user

    if request.method == "POST":
        file = request.FILES.get("myfile", None)

        if not file:
            return render(
                request,
                "main/csv_import.html",
                {"message": _("Please select a file to upload.")},
            )

        myfile = request.FILES["myfile"]
        file_path = os.path.join(settings.BASE_DIR, "import")

        filestorage = FileSystemStorage(location=str(file_path))
        filename = filestorage.save(myfile.name, myfile)
        uploaded_file_url = filestorage.url(filename)

        ch = handler()
        success = ch.csv_importer(filename=filename, user=user)

        if success:
            pass
            # Add to a scheduler TBD
            # ch.content_update()
        else:
            messages.error(request, _("Error. Unknown CSV format."))

        os.remove(os.path.join(settings.BASE_DIR, "import", filename))

        return render(
            request,
            "main/csv_import.html",
            {"uploaded_file_url": uploaded_file_url},
        )

    return render(request, "main/csv_import.html", {})


@login_required
def csv_export(request):
    user = request.user
    user_settings_model = UserSettings.objects.get(user=user)

    ch = handler()
    data = ch.csv_exporter(user=user)

    user_settings_model.last_export = timezone.now()
    user_settings_model.save()

    response = HttpResponse(data, content_type="text/csv")

    date_str = timezone.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_{user.username}_blucab-movies.csv"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


def home(request):
    if DEBUG:
        return render(
            request,
            "main/home.html",
            {
                "alert_text": _("DEBUG mode is activated! Not for production usage!"),
                "alert_type": "alert-danger",
            },
        )
    else:
        return render(request, "main/home.html", {})


@login_required
def add_movie(request):
    return render(request, "main/add_movie.html", {})


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


def movie_settings(request, movie_id):
    user = request.user

    if not user.is_superuser:
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


class CabinetCreateView(LoginRequiredMixin, CreateView):
    model = UserCabinet
    form_class = CabinetAddForm
    template_name = "main/settings_user_cabinet_add.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("view")


class CabinetDeleteView(LoginRequiredMixin, FormView):
    form_class = CabinetDeleteForm
    template_name = "main/settings_user_cabinet_delete.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        cabinet_to_delete = form.cleaned_data["cabinet"]

        if cabinet_to_delete.user == self.request.user:
            cabinet_to_delete.delete()

        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("view")
