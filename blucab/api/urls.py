# from django.conf.urls import url
from django.urls import path, include
from knox import views as knox_views
from knox import urls as knox_urls
from .views import (
    MovieListApiView,
    MovieEanApiView,
    MovieIdApiView,
    MovieUserListApiView,
    UserSettingsListApiView,
    LoginAPI,
)
    
urlpatterns = [
    path(r"auth/", include(knox_urls)), # auth/logoutall/, auth/logout/, auth/login/
    path("login/", LoginAPI.as_view()), # works better than auth/login/
    path("movie/", MovieListApiView.as_view()),
    path("movie/ean/<str:ean>", MovieEanApiView.as_view()),
    path("movie/id/<int:id>", MovieIdApiView.as_view()),
    path("movieuser/", MovieUserListApiView.as_view()),
    path("user/settings/", UserSettingsListApiView.as_view()),
]
