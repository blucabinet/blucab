from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("user/change_password/", views.change_password, name="change_password"),
    path("user/change_password/done/", views.change_password_done, name="change_password_done"),
]
