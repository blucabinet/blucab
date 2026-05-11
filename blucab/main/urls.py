from django.urls import path
from . import views
from . import cabinet
from . import views_settings
from . import csv

urlpatterns = [
    path("cab/", views.home, name="home"),
    path("cab/<str:uname>/", views.cab_uname, name="cab_uname"),
    path("", views.home, name="home"),
    path("add/", views.add_movie, name="add_movie"),
    path("view/", views.view, name="view"),
    path("legal/legal/", views.legal, name="legal"),
    path("legal/privacy/", views.privacy, name="privacy"),
    path("user/import/", csv.csv_import, name="import"),
    path("user/export/", csv.csv_export, name="export"),
    path("user/settings/", views_settings.user_settings, name="settings"),
    path(
        "user/movie_settings/<int:movie_id>",
        views_settings.user_movie_settings,
        name="user_movie_settings",
    ),
    path("user/cabinet/add/", cabinet.CabinetCreateView.as_view(), name="cabinet_add"),
    path(
        "user/cabinet/delete/",
        cabinet.CabinetDeleteView.as_view(),
        name="cabinet_delete",
    ),
    path(
        "movie_settings/<int:movie_id>",
        views_settings.movie_settings,
        name="movie_settings",
    ),
]
