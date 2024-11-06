from django.contrib import admin
from .models import Movie, MovieUserList, UserSettings

# Register your models here.
admin.site.register(Movie)
admin.site.register(MovieUserList)
admin.site.register(UserSettings)
