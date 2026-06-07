from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from .models import UserCabinet

from .forms import (
    CabinetAddForm,
    CabinetDeleteForm,
)


class CabinetCreateView(LoginRequiredMixin, CreateView):
    model = UserCabinet
    form_class = CabinetAddForm
    template_name = "main/settings_user_cabinet_add.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            context["next_url"] = next_url
        return context

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("view")


class CabinetDeleteView(LoginRequiredMixin, FormView):
    form_class = CabinetDeleteForm
    template_name = "main/settings_user_cabinet_delete.html"

    def form_valid(self, form):
        cabinet_to_delete = form.cleaned_data["cabinet"]

        if cabinet_to_delete.user == self.request.user:
            cabinet_to_delete.delete()

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            context["next_url"] = next_url
        return context

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("view")
