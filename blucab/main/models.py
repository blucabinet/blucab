from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Movie(models.Model):
    ean = models.CharField(max_length=16, verbose_name=_("EAN"))
    asin = models.CharField(max_length=16, verbose_name=_("ASIN"))
    title = models.CharField(max_length=128, verbose_name=_("Title"))
    title_clean = models.CharField(max_length=128, verbose_name=_("Title Clean"))
    format = models.CharField(max_length=16, verbose_name=_("Format"))
    release_year = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9999)],
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Release Year"),
    )
    runtime = models.IntegerField(blank=True, null=True, verbose_name=_("Runtime"))
    fsk = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("FSK"))
    fsk_nbr = models.IntegerField(
        validators=[MinValueValidator(-1), MaxValueValidator(100)],
        blank=True,
        null=True,
        default=None,
        verbose_name=_("FSK NBR"),
    )
    content = models.CharField(
        max_length=10000, blank=True, null=True, verbose_name=_("Content")
    )
    actor = models.CharField(
        max_length=500, blank=True, null=True, verbose_name=_("Actor")
    )
    regisseur = models.CharField(
        max_length=500, blank=True, null=True, verbose_name=_("Regisseur")
    )
    studio = models.CharField(
        max_length=500, blank=True, null=True, verbose_name=_("Studio")
    )
    genre = models.CharField(
        max_length=500, blank=True, null=True, verbose_name=_("Genre")
    )
    language = models.CharField(
        max_length=500, blank=True, null=True, verbose_name=_("Language")
    )
    disc_count = models.IntegerField(default=1, verbose_name=_("Disc Count"))
    movie_count = models.IntegerField(default=1, verbose_name=_("Movie Count"))
    season_count = models.IntegerField(default=0, verbose_name=_("Season Count"))
    episode_count = models.IntegerField(default=0, verbose_name=_("Episode Count"))
    is_series = models.BooleanField(default=False, verbose_name=_("Is Series"))
    is_bluray_uhd = models.BooleanField(default=False, verbose_name=_("Is Blu-ray UHD"))
    picture_available = models.BooleanField(
        default=False, verbose_name=_("Picture Available")
    )
    picture_url_original = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Picture URL Original")
    )
    picture_url_original_hd = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Picture URL Original HD")
    )
    picture_processed = models.BooleanField(
        default=False, verbose_name=_("Picture Processed")
    )
    needs_parsing = models.BooleanField(default=True, verbose_name=_("Needs Parsing"))
    imdb_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("IMDb ID")
    )

    class Meta:
        verbose_name = _("Movies")
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title_clean


class UserCabinet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="usercabinetlist",
        verbose_name=_("User"),
    )
    name = models.CharField(
        max_length=100, blank=False, null=True, verbose_name=_("Cabinet Name")
    )

    class Meta:
        unique_together = (
            "user",
            "name",
        )
        verbose_name = _("Cabinet")
        verbose_name_plural = _("Cabinets")

    def __str__(self):
        return self.name


class MovieUserList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="movieuserlist",
        null=True,
        verbose_name=_("User"),
    )
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, null=True, verbose_name=_("Movie")
    )
    activated = models.BooleanField(default=True, verbose_name=_("Activated"))
    rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        verbose_name=_("Rating"),
    )
    viewed = models.BooleanField(default=False, verbose_name=_("Viewed"))
    rented = models.BooleanField(default=False, verbose_name=_("Rented"))
    rented_to = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Rented to")
    )
    date_added = models.DateField(default=timezone.now, verbose_name=_("Date added"))
    price = models.DecimalField(
        default=0, max_digits=6, decimal_places=2, verbose_name=_("Price")
    )
    archived = models.BooleanField(default=False, verbose_name=_("Archived"))
    url_custom = models.CharField(
        max_length=1024, blank=True, null=True, verbose_name=_("Custom URL")
    )
    url_name = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Custom URL Name")
    )
    cabinet = models.ForeignKey(
        UserCabinet,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        unique_together = (
            "user",
            "movie",
        )
        verbose_name = _("User Movie List")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username}: ({self.movie.ean}) {self.movie.title_clean}"


class UserSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_profile",
        verbose_name=_("User"),
    )
    price_unit = models.CharField(
        default="€", max_length=3, blank=True, verbose_name=_("Price Unit")
    )
    days_for_new = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(730)],
        verbose_name=_("Days since adding a movie to show the new sign"),
    )
    view_is_public = models.BooleanField(
        default=False, verbose_name=_("The library can be viewed publicly")
    )
    show_view_title = models.BooleanField(
        default=True, verbose_name=_("Show Movie title")
    )
    show_view_details = models.BooleanField(
        default=True, verbose_name=_("Show Movie details")
    )
    show_view_icon_new = models.BooleanField(
        default=True, verbose_name=_("Show the new sign")
    )
    show_view_icon_rented = models.BooleanField(
        default=True, verbose_name=_("Show the rented sign")
    )
    show_view_count_disc = models.BooleanField(
        default=True, verbose_name=_("Show the number of disks")
    )
    show_view_count_movie = models.BooleanField(
        default=True, verbose_name=_("Show the number of movies")
    )
    show_view_button_details = models.BooleanField(
        default=True, verbose_name=_("Show the details button")
    )
    show_view_button_share = models.BooleanField(
        default=True, verbose_name=_("Show the share button")
    )
    last_export = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Last time an export was executed")
    )

    class Meta:
        verbose_name = _("User Settings")
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    try:
        if created:
            UserSettings.objects.create(user=instance).save()
    except Exception as err:
        print("Error creating user profile!")
