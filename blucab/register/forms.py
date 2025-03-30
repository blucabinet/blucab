from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["old_password", "password1", "password2"]
