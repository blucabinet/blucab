from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone


class Movie(models.Model):
    ean = models.CharField(max_length=16)
    asin = models.CharField(max_length=16)
    title = models.CharField(max_length=128)
    title_clean = models.CharField(max_length=128)
    format = models.CharField(max_length=16)
    release_year = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9999)],
        blank=True,
        null=True,
        default=None,
    )
    runtime = models.IntegerField(blank=True, null=True)
    fsk = models.CharField(max_length=50, blank=True, null=True)
    fsk_nbr = models.IntegerField(
        validators=[MinValueValidator(-1), MaxValueValidator(100)],
        blank=True,
        null=True,
        default=None,
    )
    content = models.CharField(max_length=10000, blank=True, null=True)
    actor = models.CharField(max_length=500, blank=True, null=True)
    regisseur = models.CharField(max_length=500, blank=True, null=True)
    studio = models.CharField(max_length=500, blank=True, null=True)
    genre = models.CharField(max_length=500, blank=True, null=True)
    language = models.CharField(max_length=500, blank=True, null=True)
    disc_count = models.IntegerField(default=1)
    movie_count = models.IntegerField(default=1)
    season_count = models.IntegerField(default=0)
    episode_count = models.IntegerField(default=0)
    is_series = models.BooleanField(default=False)
    is_bluray_uhd = models.BooleanField(default=False)
    picture_available = models.BooleanField(default=False)
    picture_url_original = models.CharField(max_length=256, blank=True, null=True)
    picture_url_original_hd = models.CharField(max_length=256, blank=True, null=True)
    picture_processed = models.BooleanField(default=False)
    needs_parsing = models.BooleanField(default=True)
    imdb_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Movies"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title_clean


class MovieUserList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="movieuserlist", null=True
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True)
    activated = models.BooleanField(default=True)
    rating = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(6)]
    )
    viewed = models.BooleanField(default=False)
    rented = models.BooleanField(default=False)
    rented_to = models.CharField(max_length=100, blank=True)
    date_added = models.DateField(default=timezone.now)
    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    class Meta:
        unique_together = (
            "user",
            "movie",
        )
        verbose_name = "User Movie List"
        verbose_name_plural = verbose_name

    def __str__(self):
        str = (
            self.user.username + ": (" + self.movie.ean + ") " + self.movie.title_clean
        )
        return str


class UserSettings(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    price_unit = models.CharField(
        default="€", max_length=3, blank=True, verbose_name="Price Unit"
    )
    days_for_new = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(730)],
        verbose_name="Days since adding a movie to show the new sign",
    )
    view_is_public = models.BooleanField(
        default=False, verbose_name="The library can be viewed publicly"
    )
    show_view_title = models.BooleanField(default=True, verbose_name="Show Movie title")
    show_view_details = models.BooleanField(
        default=True, verbose_name="Show Movie details"
    )
    show_view_icon_new = models.BooleanField(
        default=True, verbose_name="Show the new sign"
    )
    show_view_icon_rented = models.BooleanField(
        default=True, verbose_name="Show the rented sign"
    )
    show_view_count_disc = models.BooleanField(
        default=True, verbose_name="- Show the number of disks"
    )
    show_view_count_movie = models.BooleanField(
        default=True, verbose_name="- Show the number of movies"
    )
    show_view_button_details = models.BooleanField(
        default=True, verbose_name="Show the details button"
    )
    show_view_button_share = models.BooleanField(
        default=True, verbose_name="Show the share button"
    )
    last_export = models.DateTimeField(
        blank=True, null=True, verbose_name="Last time an export was executed"
    )

    class Meta:
        verbose_name = "User Settings"
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
