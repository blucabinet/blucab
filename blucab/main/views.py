from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy, reverse
from .models import UserSettings, MovieUserList, User, Movie, UserCabinet
from .forms import AddMovieForm
from contenthandler.tasks import task_add_new_movie

from environs import Env

env = Env()
env.read_env()

DEBUG = env.bool("DEBUG", False)


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
                        "url": f"{edit_url}?next={request.path}",
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
