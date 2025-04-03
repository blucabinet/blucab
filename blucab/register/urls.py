from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("user/change_password/", views.change_password, name="change_password"),
    path(
        "user/change_password/done/",
        views.change_password_done,
        name="change_password_done",
    ),
    path("user/delete/", views.delete_user, name="delete_user"),
    path("user/delete/done/", views.delete_user_done, name="delete_user_done"),
]
