# from django.conf.urls import url
from django.urls import path
from .views import (
    MovieListApiView,
    MovieApiView,
    MovieIdApiView,
    MovieUserListApiView,
    UserSettingsListApiView,
)

urlpatterns = [
    path("movie/", MovieListApiView.as_view()),
    path("movie/ean/<str:ean>", MovieApiView.as_view()),
    path("movie/id/<int:id>", MovieIdApiView.as_view()),
    path("movieuser/", MovieUserListApiView.as_view()),
    path("user/settings/", UserSettingsListApiView.as_view()),
]
