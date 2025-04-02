from django.urls import path
from . import views

urlpatterns = [
    path("cab/<str:uname>", views.index, name="index"),
    path("", views.home, name="home"),
    path("add/", views.add_movie, name="add_movie"),
    path("view/", views.view, name="view"),
    path("legal/legal/", views.legal, name="legal"),
    path("legal/privacy/", views.privacy, name="privacy"),
    path("user/import/", views.csv_import, name="import"),
    path("user/settings/", views.user_settings, name="settings"),
]
