from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy, reverse
from .models import UserSettings, MovieUserList, User, Movie, UserCabinet, MovieViewLog
from .forms import AddMovieForm, MovieErrorReportForm
from contenthandler.tasks import task_add_new_movie

from environs import Env

env = Env()
env.read_env()

DEBUG = env.bool("DEBUG", False)
ALLOW_MOVIE_ERROR_REPORT = env.bool("BLUCAB_ALLOW_MOVIE_ERROR_REPORT", True)


def legal(request):
    return render(request, "legal/legal.html", {})


def privacy(request):
    return render(request, "legal/privacy.html", {})


def cab_uname(request, uname):
    request_user = request.user
    user_id_query = User.objects.filter(username=uname).first()

    if user_id_query is None:
        return render(request, "error/403_user_not_public.html", status=403)

    user = user_id_query.id
    usersettings = UserSettings.objects.filter(user=user).first()
    view_is_public = usersettings.view_is_public

    if not view_is_public:
        return render(request, "error/403_user_not_public.html", status=403)

    movieuserlist = MovieUserList.objects.filter(user=user, activated=True)
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
            "allow_movie_error_report": ALLOW_MOVIE_ERROR_REPORT,
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

    movieuserlist = MovieUserList.objects.filter(user=user, activated=True)
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
            "allow_movie_error_report": ALLOW_MOVIE_ERROR_REPORT,
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
def view_simple(request):
    user = request.user

    movieuserlist = MovieUserList.objects.filter(user=user)
    cabinets = UserCabinet.objects.filter(user=user)

    if request.method == "POST":
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected_movies")

        if action and selected_ids:
            selected_movies = movieuserlist.filter(id__in=selected_ids)

            if action == "set_activated":
                selected_movies.update(activated=True)

            elif action == "set_rented":
                selected_movies.update(rented=True)

            elif action == "set_archived":
                selected_movies.update(archived=True)

            elif action == "set_viewed":
                selected_movies.update(viewed=True)

            elif action == "set_cabinet":
                cabinet_id = request.POST.get("cabinet_id")
                if cabinet_id:
                    if cabinets.filter(id=cabinet_id).exists():
                        selected_movies.update(cabinet_id=cabinet_id)
                    else:
                        messages.error(request, "Invalid cabinet selection.")
                        return redirect("view_simple")

            elif action == "unset_activated":
                selected_movies.update(activated=False)

            elif action == "unset_rented":
                selected_movies.update(rented=False)

            elif action == "unset_archived":
                selected_movies.update(archived=False)

            elif action == "unset_viewed":
                selected_movies.update(viewed=False)

            elif action == "unset_cabinet":
                selected_movies.update(cabinet=None)

            elif action == "delete":
                deleted_count, _ = selected_movies.delete()
                messages.warning(
                    request,
                    f"Successfully deleted {deleted_count} movies from your collection.",
                )
                return redirect("view_simple")

            messages.success(
                request, f"Action successfully executed for {len(selected_ids)} movies."
            )

        return redirect("view_simple")

    movieuserlist = movieuserlist.order_by("movie__title_clean")

    return render(
        request,
        "main/view_list.html",
        {
            "movieuserlist": movieuserlist,
            "cabinets": cabinets,
        },
    )


def home(request):
    top_movies = (
        Movie.objects.annotate(added_count=Count("movieuserlist"))
        .filter(added_count__gt=0)
        .order_by("-added_count", "-id")[:10]
    )

    context = {
        "top_movies": top_movies,
    }

    if DEBUG:
        context["alert_text"] = _("DEBUG mode is activated! Not for production usage!")
        context["alert_type"] = "alert-danger"
        return render(request, "main/home.html", context)
    else:
        return render(request, "main/home.html", context)


@login_required
def add_movie(request):
    if request.method == "POST" and "confirm_add" in request.POST:
        ean = request.POST.get("ean")
        try:
            movie = Movie.objects.get(ean=ean)
            obj, created = MovieUserList.objects.get_or_create(
                user=request.user, movie=movie
            )

            if created:
                url = str(reverse_lazy("view"))
                title = movie.title_clean

                msg = _(
                    "Movie '%(title)s' successfully added to your <a href='%(url)s' class='alert-link'>collection</a>"
                ) % {
                    "url": f"{url}",
                    "title": title,
                }

                messages.success(request, mark_safe(msg))
                return redirect("add_movie")
            else:
                messages.info(request, _("This movie is already in your collection."))
                return redirect("add_movie")

        except Movie.DoesNotExist:
            messages.error(request, _("Error: Movie not found."))
        return redirect("add_movie")

    # Process the initial EAN input
    if request.method == "POST":
        form = AddMovieForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"].strip()

            # Check if it's an exact EAN match first
            movie_by_ean = Movie.objects.filter(ean=query).first()
            if movie_by_ean:
                if MovieUserList.objects.filter(
                    user=request.user, movie=movie_by_ean
                ).exists():
                    edit_url = str(
                        reverse_lazy("user_movie_settings", args=[movie_by_ean.id])
                    )

                    msg = _(
                        "The movie '%(title)s' is already in your collection. <a href='%(url)s' class='alert-link'>Edit</a>"
                    ) % {
                        "title": movie_by_ean.title_clean,
                        "next_url": f"{edit_url}?next={request.path}",
                    }

                    messages.warning(request, mark_safe(msg))
                    return redirect("add_movie")
                return render(
                    request,
                    "main/add_movie_confirm.html",
                    {"movie": movie_by_ean, "ean": query},
                )

            # Verify if it's an EAN
            if query.isdigit() and len(query) >= 8 and len(query) <= 13:
                task_add_new_movie.delay(query)
                messages.info(
                    request,
                    _(
                        "EAN not found. The movie is being fetched in the background. Please check back later."
                    ),
                )
                url = reverse("add_movie")
                return redirect(f"{url}?query={query}")

            movies = Movie.objects.filter(
                Q(title__icontains=query) | Q(title_clean__icontains=query)
            ).distinct()

            if movies.exists():
                user_movie_eans = MovieUserList.objects.filter(
                    user=request.user, movie__in=movies
                ).values_list("movie__ean", flat=True)

                return render(
                    request,
                    "main/add_movie_results.html",
                    {
                        "movies": movies,
                        "query": query,
                        "user_movie_eans": user_movie_eans,
                    },
                )
            else:
                messages.warning(request, _("No movies found matching your search."))
                return redirect("add_movie")
    else:
        initial_query = request.GET.get("query", "")
        form = AddMovieForm(initial={"query": initial_query})

    return render(request, "main/add_movie.html", {"form": form})


@login_required
def add_view_log(request, mu_id):
    movie_user_entry = get_object_or_404(MovieUserList, id=mu_id, user=request.user)
    next_url = request.GET.get("next", "view")

    if request.method == "POST":
        view_date = request.POST.get("view_date")
        watched_with = request.POST.get("watched_with")
        comment = request.POST.get("comment")

        if view_date:
            MovieViewLog.objects.create(
                movie_user_list=movie_user_entry,
                view_date=view_date,
                watched_with=watched_with,
                comment=comment,
            )

            if not movie_user_entry.viewed:
                movie_user_entry.viewed = True
                movie_user_entry.save()

            messages.success(request, _("Viewing history updated."))

    return redirect(next_url)


@login_required
def delete_view_log(request, log_id):
    next_url = request.GET.get("next", "view")

    if request.method == "POST":
        log = get_object_or_404(
            MovieViewLog, id=log_id, movie_user_list__user=request.user
        )
        movie_user_entry = log.movie_user_list
        log.delete()

        if not movie_user_entry.view_logs.exists():
            movie_user_entry.viewed = False
            movie_user_entry.save()

        messages.success(request, _("Viewing log entry deleted."))

    return redirect(next_url)


@login_required
def report_movie_error(request, movie_id):
    if not ALLOW_MOVIE_ERROR_REPORT:
        return redirect("view")

    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == "POST":
        form = MovieErrorReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.movie = movie
            report.user = request.user
            report.save()

        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("view")
    else:
        form = MovieErrorReportForm()

    next_url = request.GET.get("next", "")

    return render(
        request,
        "main/report_movie_error.html",
        {
            "form": form,
            "movie": movie,
            "next_url": next_url,
        },
    )
