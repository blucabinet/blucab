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


admin.site.register(MovieUserList)
admin.site.register(UserSettings)
admin.site.register(UserCabinet)
admin.site.register(FailedAddMovie)
admin.site.register(MovieViewLog)
admin.site.register(MovieErrorReport)

admin.site.site_title = _("blucab site admin")
admin.site.site_header = _("blucab administration")
