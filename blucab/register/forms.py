from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label=(_("Email")), required=True)
    email_confirm = forms.EmailField(label=(_("Email confirmation")), required=True)

    captcha = CaptchaField(label=_("Are you a human?"))

    class Meta:
        model = User
        fields = ["username", "email", "email_confirm", "password1", "password2", "captcha"]

    def clean(self):
        """
        Check if the email is entered correctly in both fields.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_confirm = cleaned_data.get("email_confirm")

        if email and email_confirm and email != email_confirm:
            self.add_error('email_confirm', _("The Email confirmation does not match the Email."))
        
        return cleaned_data

    def clean_email(self):
        """
        Check if the email is already used by another account.
        The check is case-insensitive."
        """
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            self.add_error('email', _("This email address is already used by another account."))
        return email


class ResetPasswordForm(PasswordResetForm):
    captcha = CaptchaField(label=_("Are you a human?"))


class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["old_password", "password1", "password2"]


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        """
        Check if the email is already used by another account.
        The check is case-insensitive."
        """
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("This email address is already used by another account."))
        return email

