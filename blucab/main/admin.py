from django.contrib import admin
from .models import Movie, MovieUserList, UserSettings, UserCabinet
from django.utils.translation import gettext as _

# Register your models here.
admin.site.register(Movie)
admin.site.register(MovieUserList)
admin.site.register(UserSettings)
admin.site.register(UserCabinet)

admin.site.site_title = _("blucab site admin")
admin.site.site_header = _("blucab administration")
