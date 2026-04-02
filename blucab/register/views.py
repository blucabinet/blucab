from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext as _
from django.utils.encoding import force_bytes, force_str
from .forms import RegisterForm, ChangePasswordForm

from environs import Env
env = Env()
env.read_env()

ALLOW_REGISTRATION = env.bool("BLUCAB_ALLOW_REGISTER", False)
EMAIL_ENABLED = env.bool("DJANGO_EMAIL_ENABLE", False)


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
                mail_subject = _("[blucab] Activate your blucab Account")
                message = render_to_string('email/account_activation.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'protocol': 'https:' if request.is_secure() else 'http:',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()

                messages.info(request, _(f'You should have received an email to confirm your email address and complete the registration.'))
                return redirect('login')
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
        messages.success(request, _("Thank you for the confirmation. You can now log in."))
        return redirect('login')
    else:
        messages.error(request, _("The activation link is invalid or has expired!"))
        return redirect('register')


def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _("Your password was successfully updated!"))
            return redirect("change_password_done")
        else:
            messages.error(request, _("Please correct the error below."))
    else:
        form = ChangePasswordForm(request.user)

    return render(request, "register/change_password.html", {"form": form})


def change_password_done(request):
    return render(request, "register/change_password_done.html", {})


def delete_user(request):
    user = request.user

    if not user.is_authenticated:
        return render(request, "error/403.html", {})

    if request.method == "GET":
        return render(request, "register/delete_user_confirm.html", {})
    elif request.method == "POST":
        if EMAIL_ENABLED:
            mail_subject = _("[blucab] blucab Account deleted")
            message = render_to_string(
                "email/account_deletion.html",
                {
                    "user": user,
                },
            )
            to_email = user.email
            email = EmailMessage(mail_subject, message, to=[to_email])
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
