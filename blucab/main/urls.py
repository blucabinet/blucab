from django.urls import path
from . import views

urlpatterns = [
    path("cab/", views.home, name="home"),
    path("cab/<str:uname>", views.cab_uname, name="cab_uname"),
    path("", views.home, name="home"),
    path("add/", views.add_movie, name="add_movie"),
    path("view/", views.view, name="view"),
    path("legal/legal/", views.legal, name="legal"),
    path("legal/privacy/", views.privacy, name="privacy"),
    path("user/import/", views.csv_import, name="import"),
    path("user/settings/", views.user_settings, name="settings"),
    path("user/movie_settings/<int:movie_id>", views.user_movie_settings, name="user_movie_settings"),
    path("movie_settings/<int:movie_id>", views.movie_settings, name="movie_settings"),
]
