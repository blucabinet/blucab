# from django.conf.urls import url
from django.urls import path
from .views import (
    MovieListApiView,
    MovieApiView,
)

urlpatterns = [
    path("movie/", MovieListApiView.as_view()),
    path("movie/<str:ean>", MovieApiView.as_view()),
]
