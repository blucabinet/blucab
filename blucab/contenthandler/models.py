from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from main.models import Movie


class FailedAddMovie(models.Model):
    ean = models.CharField(max_length=16, verbose_name=_("EAN"))
    date_added = models.DateTimeField(
        default=timezone.now, verbose_name=_("Date added")
    )
    is_movie_update = models.BooleanField(
        default=False, verbose_name=_("Is Existing Movie")
    )
    checked = models.BooleanField(default=False, verbose_name=_("Checked"))
    movie = models.ForeignKey(
        Movie, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Movie")
    )

    class Meta:
        verbose_name = _("Failed Movie Import")
        verbose_name_plural = _("Failed Movie Imports")

    def __str__(self):
        return f"{self.ean} - {self.date_added.strftime('%Y-%m-%d %H:%M')}"
