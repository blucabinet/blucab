from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label=(_("Email")), required=True)
    email_confirm = forms.EmailField(label=(_("Email confirmation")), required=True)

    class Meta:
        model = User
        fields = ["username", "email", "email_confirm", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_confirm = cleaned_data.get("email_confirm")

        if email and email_confirm and email != email_confirm:
            self.add_error('email_confirm', _("The Email confirmation does not match the Email."))
        
        return cleaned_data


class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["old_password", "password1", "password2"]
