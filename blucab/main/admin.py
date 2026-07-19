from django.contrib import admin
from .models import (
    Movie,
    MovieUserList,
    UserSettings,
    UserCabinet,
    MovieViewLog,
    MovieErrorReport,
    Format,
    Language,
    Actor,
    Studio,
    Director,
    ContentRating,
)
from contenthandler.models import FailedAddMovie
from django.utils.translation import gettext as _


# Register your models here.
@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(ContentRating)
class ContentRatingAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title_clean", "ean", "release_year")
    search_fields = ("title_clean", "ean", "asin")

    autocomplete_fields = [
        "format",
        "content_rating",
        "actors",
        "directors",
        "studios",
        "languages",
    ]


@admin.register(UserCabinet)
class UserCabinetAdmin(admin.ModelAdmin):
    search_fields = ["name", "user__username"]
    autocomplete_fields = ["user"]


@admin.register(MovieUserList)
class MovieUserListAdmin(admin.ModelAdmin):
    search_fields = ["user__username", "movie__title_clean", "movie__ean"]
    autocomplete_fields = ["user", "movie", "cabinet"]


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]


@admin.register(MovieViewLog)
class MovieViewLogAdmin(admin.ModelAdmin):
    autocomplete_fields = ["movie_user_list"]


@admin.register(MovieErrorReport)
class MovieErrorReportAdmin(admin.ModelAdmin):
    list_display = ("movie", "user", "created_at", "checked_at")
    autocomplete_fields = ["movie", "user", "checked_by"]


@admin.register(FailedAddMovie)
class FailedAddMovieAdmin(admin.ModelAdmin):
    list_display = ("ean", "date_added", "is_movie_update", "checked")
    search_fields = ["ean", "movie__title_clean"]
    autocomplete_fields = ["movie"]


admin.site.site_title = _("blucab site admin")
admin.site.site_header = _("blucab administration")
