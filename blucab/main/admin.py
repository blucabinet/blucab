from django.contrib import admin
from .models import ToDoList, Item, Movie, MovieUserList, UserSettings

# Register your models here.
admin.site.register(ToDoList)
admin.site.register(Item)
admin.site.register(Movie)
admin.site.register(MovieUserList)
admin.site.register(UserSettings)
