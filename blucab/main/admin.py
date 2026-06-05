from django.contrib import admin
from .models import (
    Movie,
    MovieUserList,
    UserSettings,
    UserCabinet,
    MovieViewLog,
    MovieErrorReport,
)
from contenthandler.models import FailedAddMovie
from django.utils.translation import gettext as _

# Register your models here.
admin.site.register(Movie)
admin.site.register(MovieUserList)
admin.site.register(UserSettings)
admin.site.register(UserCabinet)
admin.site.register(FailedAddMovie)
admin.site.register(MovieViewLog)
admin.site.register(MovieErrorReport)

admin.site.site_title = _("blucab site admin")
admin.site.site_header = _("blucab administration")
