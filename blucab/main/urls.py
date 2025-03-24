from django.urls import path
from . import views

urlpatterns = [
    path("cab/<str:uname>", views.index, name="index"),
    path("", views.home, name="home"),
    path("view/", views.view, name="view"),
    path("import/", views.csv_import, name="import"),
    path("legal/legal/", views.legal, name="legal"),
    path("legal/privacy/", views.privacy, name="privacy"),
    path("user/settings/", views.settings, name="settings"),
]
