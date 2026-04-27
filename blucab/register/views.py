from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_bytes, force_str
from .forms import RegisterForm, ChangePasswordForm, EmailChangeForm
from .tokens import email_change_token_generator

from environs import Env

env = Env()
env.read_env()

ALLOW_REGISTRATION = env.bool("BLUCAB_ALLOW_REGISTER", False)
EMAIL_ENABLED = env.bool("DJANGO_EMAIL_ENABLE", False)
EMAIL_FROM_NOREPLY = env.str("DJANGO_EMAIL_FROM_NOREPLY", "no-reply@localhost")
EMAIL_SUBJECT_PREFIX = env.str("DJANGO_EMAIL_SUBJECT_PREFIX", "[blucab] ")


def register(request):
    if not ALLOW_REGISTRATION:
        return render(request, "error/403.html", {})

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            if EMAIL_ENABLED:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                mail_subject = EMAIL_SUBJECT_PREFIX + _("Activate your blucab Account")
                message = render_to_string(
                    "email/account_activation.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "protocol": "https:" if request.is_secure() else "http:",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    },
                )
                to_email = form.cleaned_data.get("email")
                email = EmailMessage(
                    subject=mail_subject,
                    body=message,
                    to=[to_email],
                    from_email=EMAIL_FROM_NOREPLY,
                )
                email.send()

                messages.info(
                    request,
                    _(
                        f"You should have received an email to confirm your email address and complete the registration."
                    ),
                )
                return redirect("login")
            else:
                form.save()
                # Auto login after registration
                new_user = authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"],
                )
                login(request, new_user)

                return redirect("settings")
    else:
        form = RegisterForm()

    return render(request, "register/register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, _("Thank you for the confirmation. You can now log in.")
        )
        return redirect("login")
    else:
        messages.error(request, _("The activation link is invalid or has expired!"))
        return redirect("register")


@login_required
def change_password(request):
    user = request.user

    if request.method == "POST":
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            user_form = form.save()
            update_session_auth_hash(request, user_form)
            messages.success(request, _("Your password was successfully updated!"))
            return redirect("change_password_done")
        else:
            messages.error(request, _("Please correct the error below."))
    else:
        form = ChangePasswordForm(user)

    return render(request, "register/change_password.html", {"form": form})


@login_required
def change_password_done(request):
    return render(request, "register/change_password_done.html", {})


@login_required
def delete_user(request):
    user = request.user

    if request.method == "GET":
        return render(request, "register/delete_user_confirm.html", {})
    elif request.method == "POST":
        if EMAIL_ENABLED:
            mail_subject = EMAIL_SUBJECT_PREFIX + _("blucab Account deleted")
            message = render_to_string(
                "email/account_deletion.html",
                {
                    "user": user,
                },
            )
            to_email = user.email
            email = EmailMessage(
                subject=mail_subject,
                body=message,
                to=[to_email],
                from_email=EMAIL_FROM_NOREPLY,
            )
            email.send()

            messages.success(
                request, _("A confirmation email has been sent to your email address.")
            )

        user_object = User.objects.get(username=user)
        user_object.delete()
        update_session_auth_hash(request, user)

        return redirect("delete_user_done")


def delete_user_done(request):
    return render(request, "register/delete_user_done.html", {})


@login_required
def change_email_request(request):
    user = request.user

    if request.method == "POST":
        form = EmailChangeForm(request.POST, instance=user)
        if form.is_valid():
            if EMAIL_ENABLED:
                new_email = form.cleaned_data.get("email")

                current_site = get_current_site(request)
                mail_subject = EMAIL_SUBJECT_PREFIX + _("Verify your new email address")
                message = render_to_string(
                    "email/email_change.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "protocol": "https:" if request.is_secure() else "http:",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": email_change_token_generator.make_token(user),
                        "new_email": urlsafe_base64_encode(force_bytes(new_email)),
                    },
                )
                email = EmailMessage(
                    subject=mail_subject,
                    body=message,
                    to=[new_email],
                    from_email=EMAIL_FROM_NOREPLY,
                )
                email.send()

                messages.info(
                    request,
                    _(
                        "A confirmation email has been sent to your new email address. Please confirm the change by clicking the link in the email."
                    ),
                )
                return redirect("settings")
            else:
                form.save()
                messages.success(
                    request, _("Your email address has been updated successfully.")
                )
                return redirect("settings")
    else:
        form = EmailChangeForm(instance=request.user)

    return render(request, "register/change_email.html", {"form": form})


def change_email_confirm(request, uidb64, token, new_email_b64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        new_email = force_str(urlsafe_base64_decode(new_email_b64))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_change_token_generator.check_token(user, token):
        user.email = new_email
        user.save()
        messages.success(
            request, _("Your email address has been updated successfully.")
        )
        return redirect("settings")
    else:
        messages.error(request, _("The activation link is invalid or has expired!"))
        return redirect("settings")
