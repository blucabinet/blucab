from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone


# Create your models here.
class ToDoList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="todolist", null=True
    )
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Item(models.Model):
    todolist = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    complete = models.BooleanField()

    def __str__(self):
        return self.text


class Movie(models.Model):
    ean = models.CharField(max_length=16)
    asin = models.CharField(max_length=16)
    title = models.CharField(max_length=128)
    title_clean = models.CharField(max_length=128)
    format = models.CharField(max_length=16)
    release_year = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9999)]
    )
    runtime = models.IntegerField()
    fsk = models.CharField(max_length=50, blank=True)
    content = models.CharField(max_length=10000, blank=True)
    actor = models.CharField(max_length=500, blank=True)
    regisseur = models.CharField(max_length=100, blank=True)
    studio = models.CharField(max_length=100, blank=True)
    genre = models.CharField(max_length=200, blank=True)
    language = models.CharField(max_length=200, blank=True)
    disc_count = models.IntegerField(default=1)
    movie_count = models.IntegerField(default=1)
    season_count = models.IntegerField(default=0)
    episode_count = models.IntegerField(default=0)
    is_series = models.BooleanField(default=False)
    picture_available = models.BooleanField(default=False)

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
        str = self.user.username + ": " + self.movie.title_clean
        return str


class UserSettings(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    price_unit = models.CharField(default="€", max_length=3, blank=True)
    days_for_new = models.IntegerField(
        default=30, validators=[MinValueValidator(0), MaxValueValidator(730)]
    )
    view_is_public = models.BooleanField(default=False)
    show_view_title = models.BooleanField(default=True)
    show_view_details = models.BooleanField(default=True)
    show_view_icon_new = models.BooleanField(default=True)
    show_view_icon_rented = models.BooleanField(default=True)
    show_view_count_disc = models.BooleanField(default=True)
    show_view_count_movie = models.BooleanField(default=True)
    show_view_button_details = models.BooleanField(default=True)

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
