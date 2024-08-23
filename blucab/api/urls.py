# from django.conf.urls import url
from django.urls import path
from .views import (
    MovieListApiView,
)

urlpatterns = [
    path("movie", MovieListApiView.as_view()),
]
