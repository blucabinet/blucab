from django.db import transaction
from django.db.models import Count, F
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _

from main.models import (
    UserSettings,
    UserCabinet,
    MovieUserList,
    Movie,
)
from inventory.models import InventorySession, InventoryScan
from contenthandler.tasks import task_add_new_movie

from decimal import Decimal, InvalidOperation


# Create your views here.
def _save_inventory_session_defaults(request, session, user):
    update_fields = []

    if "batch_number" in request.POST:
        raw_batch_number = request.POST.get("batch_number", "").strip()

        try:
            session.current_batch_number = (
                int(raw_batch_number) if raw_batch_number else None
            )
        except ValueError:
            return _("Enter a valid batch number.")

        update_fields.append("current_batch_number")

    for field_name in ("default_viewed", "default_rented"):
        if field_name not in request.POST:
            continue

        raw_value = request.POST.get(field_name, "")

        if raw_value == "":
            value = None
        elif raw_value == "true":
            value = True
        elif raw_value == "false":
            value = False
        else:
            return _("Select a valid default value.")

        setattr(session, field_name, value)
        update_fields.append(field_name)

    if "default_cabinet" in request.POST:
        raw_cabinet_id = request.POST.get("default_cabinet", "").strip()

        if raw_cabinet_id:
            try:
                cabinet_id = int(raw_cabinet_id)
                cabinet = UserCabinet.objects.get(
                    pk=cabinet_id,
                    user=user,
                )
            except (ValueError, UserCabinet.DoesNotExist):
                return _("Select a valid cabinet.")
        else:
            cabinet = None

        session.default_cabinet = cabinet
        update_fields.append("default_cabinet")

    if update_fields:
        session.save(update_fields=update_fields)

    return None


def _inventory_movie_default_values(session):
    values = {}

    if session.default_viewed is not None:
        values["viewed"] = session.default_viewed

    if session.default_rented is not None:
        values["rented"] = session.default_rented

    if session.default_cabinet_id is not None:
        values["cabinet"] = session.default_cabinet

    return values


@login_required
def inventory_check(request):
    user = request.user
    session, created_session = InventorySession.objects.get_or_create(user=user)
    error = _save_inventory_session_defaults(request, session, user)

    if error:
        messages.error(request, error)
        return redirect("inventory_check")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "reset":
            session.scans.all().delete()
            session.started_at = timezone.now()
            session.save(update_fields=["started_at"])
            messages.success(request, _("The inventory check has been reset."))
            return redirect("inventory_check")

        if action == "check_manually":
            entry = get_object_or_404(
                MovieUserList.objects.select_related("movie"),
                pk=request.POST.get("entry_id"),
                user=user,
            )

            now = timezone.now()

            scan, created = InventoryScan.objects.get_or_create(
                session=session,
                ean=entry.movie.ean,
                defaults={
                    "movie": entry.movie,
                    "batch_number": session.current_batch_number,
                    "scan_count": 1,
                    "first_scanned_at": now,
                    "last_scanned_at": now,
                },
            )

            if created:
                default_values = _inventory_movie_default_values(session)

                if default_values:
                    MovieUserList.objects.filter(
                        user=user,
                        movie__ean=entry.movie.ean,
                    ).update(**default_values)

            if created:
                messages.success(
                    request,
                    _("Movie manually checked: %(title)s")
                    % {"title": entry.movie.title_clean},
                )
            else:
                messages.info(
                    request,
                    _("This movie has already been checked."),
                )

            return redirect("inventory_check")

        if action == "add_to_collection":
            scan = get_object_or_404(
                InventoryScan,
                pk=request.POST.get("scan_id"),
                session=session,
            )
            existing_entry = MovieUserList.objects.filter(
                user=user,
                movie__ean=scan.ean,
            ).first()

            if existing_entry:
                messages.info(
                    request,
                    _("This movie is already in your collection."),
                )
                return redirect("inventory_check")

            movie = (
                scan.movie or Movie.objects.filter(ean=scan.ean).order_by("pk").first()
            )

            if movie is None:
                messages.warning(
                    request,
                    _("The movie data is not available yet. Please try again later."),
                )
                return redirect("inventory_check")

            created_entry, created = MovieUserList.objects.get_or_create(
                user=user,
                movie=movie,
                defaults=_inventory_movie_default_values(session),
            )

            if created:
                messages.success(
                    request,
                    _("%(title)s was added to your collection.")
                    % {"title": movie.title_clean},
                )
            else:
                messages.info(
                    request,
                    _("This movie is already in your collection."),
                )

            return redirect("inventory_check")

        if action == "scan":
            raw_ean = request.POST.get("ean", "").strip()
            ean = "".join(raw_ean.split()).replace("-", "")

            if not ean.isascii() or not ean.isdigit() or not 8 <= len(ean) <= 14:
                messages.error(
                    request,
                    _("Enter a valid EAN/GTIN containing 8 to 14 digits."),
                )
                return redirect("inventory_check")

            movie = Movie.objects.filter(ean=ean).order_by("pk").first()
            now = timezone.now()

            with transaction.atomic():
                scan, created = InventoryScan.objects.get_or_create(
                    session=session,
                    ean=ean,
                    defaults={
                        "movie": movie,
                        "batch_number": session.current_batch_number,
                        "first_scanned_at": now,
                        "last_scanned_at": now,
                    },
                )

                if created:
                    default_values = _inventory_movie_default_values(session)

                    if default_values:
                        MovieUserList.objects.filter(
                            user=user,
                            movie__ean=ean,
                        ).update(**default_values)

                if not created:
                    update_values = {
                        "scan_count": F("scan_count") + 1,
                        "last_scanned_at": now,
                    }

                    if movie and scan.movie_id is None:
                        update_values["movie"] = movie

                    InventoryScan.objects.filter(pk=scan.pk).update(**update_values)
                    scan.refresh_from_db()

            if scan.scan_count > 1:
                messages.warning(
                    request,
                    _("This EAN/GTIN was scanned more than once (%(count)s scans).")
                    % {"count": scan.scan_count},
                )
            elif MovieUserList.objects.filter(
                user=user,
                movie__ean=ean,
            ).exists():
                existing_movie = (
                    MovieUserList.objects.filter(
                        user=user,
                        movie__ean=ean,
                    )
                    .first()
                    .movie
                )

                messages.success(
                    request,
                    _("Movie found in your collection: %(title)s")
                    % {"title": existing_movie.title_clean},
                )
            elif movie:
                messages.warning(
                    request,
                    _(
                        "Movie found in the database but not in your collection: %(title)s"
                    )
                    % {"title": movie.title_clean},
                )
            else:
                if created:
                    try:
                        task_add_new_movie.delay(ean)
                    except Exception:
                        messages.warning(
                            request,
                            _(
                                "The EAN/GTIN was scanned, but the movie lookup could not be started."
                            ),
                        )
                    else:
                        messages.info(
                            request,
                            _(
                                "Movie not found yet. A background lookup has been started for EAN/GTIN %(ean)s."
                            )
                            % {"ean": ean},
                        )
                else:
                    messages.info(
                        request,
                        _("EAN/GTIN %(ean)s is recorded. Movie data is still pending.")
                        % {"ean": ean},
                    )

            return redirect("inventory_check")

        messages.error(request, _("Unknown inventory action."))
        return redirect("inventory_check")

    movie_entries = list(
        MovieUserList.objects.filter(user=user)
        .select_related("movie", "movie__format", "cabinet")
        .order_by("movie__title_clean", "pk")
    )

    entries_by_ean = {}
    for entry in movie_entries:
        entries_by_ean.setdefault(entry.movie.ean, []).append(entry)

    scans = list(
        session.scans.select_related("movie").order_by("first_scanned_at", "pk")
    )

    unknown_scans = []
    pending_scans = []

    for scan in scans:
        matching_entries = entries_by_ean.get(scan.ean, [])

        if matching_entries:
            scan.display_movie = matching_entries[0].movie
            scan.in_collection = True
            continue

        movie = scan.movie

        if movie is None:
            movie = Movie.objects.filter(ean=scan.ean).order_by("pk").first()

            if movie:
                InventoryScan.objects.filter(
                    pk=scan.pk,
                    movie__isnull=True,
                ).update(movie=movie)
                scan.movie = movie

        scan.display_movie = movie
        scan.in_collection = False

        if movie:
            unknown_scans.append(scan)
        else:
            pending_scans.append(scan)

    scanned_eans = {scan.ean for scan in scans}

    unchecked_movies = [
        entry for entry in movie_entries if entry.movie.ean not in scanned_eans
    ]

    checked_movies = [
        entry for entry in movie_entries if entry.movie.ean in scanned_eans
    ]

    duplicate_counts = {
        row["movie__ean"]: row["entry_count"]
        for row in MovieUserList.objects.filter(user=user)
        .values("movie__ean")
        .annotate(entry_count=Count("pk"))
        .filter(entry_count__gt=1)
    }

    duplicate_rows_by_ean = {}

    # Find movies with multiple entries in the user's collection.
    for ean, entry_count in duplicate_counts.items():
        entries = entries_by_ean.get(ean, [])
        movie = entries[0].movie if entries else None

        duplicate_rows_by_ean[ean] = {
            "ean": ean,
            "movie": movie,
            "collection_count": entry_count,
            "scan_count": None,
        }

    # Merge movies that have been scanned more than once.
    for scan in scans:
        if scan.scan_count <= 1:
            continue

        row = duplicate_rows_by_ean.setdefault(
            scan.ean,
            {
                "ean": scan.ean,
                "movie": scan.display_movie,
                "collection_count": len(entries_by_ean.get(scan.ean, [])),
                "scan_count": None,
            },
        )

        if row["movie"] is None and scan.display_movie:
            row["movie"] = scan.display_movie

        row["scan_count"] = scan.scan_count

    duplicate_rows = sorted(
        duplicate_rows_by_ean.values(),
        key=lambda row: (
            row["movie"].title_clean.casefold() if row["movie"] else "",
            row["ean"],
        ),
    )

    total_count = len(movie_entries)
    checked_count = len(checked_movies)

    progress_percent = round(checked_count * 100 / total_count) if total_count else 0

    return render(
        request,
        "inventory/inventory_check.html",
        {
            "inventory_session": session,
            "cabinets": UserCabinet.objects.filter(user=user).order_by("name"),
            "movie_entries": movie_entries,
            "unchecked_movies": unchecked_movies,
            "checked_movies": checked_movies,
            "unknown_scans": unknown_scans,
            "pending_scans": pending_scans,
            "duplicate_rows": duplicate_rows,
            "total_count": total_count,
            "checked_count": checked_count,
            "unchecked_count": len(unchecked_movies),
            "progress_percent": progress_percent,
            "price_unit": (
                UserSettings.objects.filter(user=user)
                .values_list("price_unit", flat=True)
                .first()
                or "€"
            ),
            "default_viewed_value": (
                ""
                if session.default_viewed is None
                else "true" if session.default_viewed else "false"
            ),
            "default_rented_value": (
                ""
                if session.default_rented is None
                else "true" if session.default_rented else "false"
            ),
        },
    )


@login_required
def inventory_update(request, entry_id):
    if request.method != "POST":
        return redirect("inventory_check")

    entry = get_object_or_404(
        MovieUserList,
        pk=entry_id,
        user=request.user,
    )

    cabinet_id = request.POST.get("cabinet_id", "").strip()

    if cabinet_id:
        cabinet = get_object_or_404(
            UserCabinet,
            pk=cabinet_id,
            user=request.user,
        )
    else:
        cabinet = None

    try:
        price = Decimal(request.POST.get("price", "").strip())

        if (
            not price.is_finite()
            or price < 0
            or price > Decimal("9999.99")
            or price.as_tuple().exponent < -2
        ):
            raise InvalidOperation

    except (InvalidOperation, ValueError):
        messages.error(
            request,
            _("Enter a valid price with up to two decimal places."),
        )
        return redirect("inventory_check")

    date_added = parse_date(request.POST.get("date_added", ""))

    if date_added is None:
        messages.error(request, _("Enter a valid date added."))
        return redirect("inventory_check")

    entry.rented = request.POST.get("rented") == "true"
    entry.viewed = request.POST.get("viewed") == "true"
    entry.cabinet = cabinet
    entry.price = price
    entry.date_added = date_added

    entry.save(
        update_fields=[
            "rented",
            "viewed",
            "cabinet",
            "price",
            "date_added",
        ]
    )

    messages.success(
        request,
        _("Changes for %(title)s were saved.") % {"title": entry.movie.title_clean},
    )

    return redirect("inventory_check")
