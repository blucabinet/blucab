from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("user/register/", views.register, name="register"),
    path("user/activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("user/password_change/", views.change_password, name="change_password"),
    path(
        "user/password_change/done/",
        views.change_password_done,
        name="change_password_done",
    ),
    path("user/delete/", views.delete_user, name="delete_user"),
    path("user/delete/done/", views.delete_user_done, name="delete_user_done"),
    path(
        "user/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="register/password_reset.html",
            email_template_name='email/password_reset_email.html',
            subject_template_name='email/password_reset_subject.txt'
        ),
        name="password_reset",
    ),
    path(
        "user/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="register/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "user/password_reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="register/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "user/password_reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="register/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
