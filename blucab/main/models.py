from django.db import models
from django.contrib.auth.models import User


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
    release = models.CharField(max_length=4, blank=True)
    runtime = models.CharField(max_length=5, blank=True)
    fsk = models.CharField(max_length=50, blank=True)
    content = models.CharField(max_length=10000, blank=True)
    actor = models.CharField(max_length=500, blank=True)
    regisseur = models.CharField(max_length=100, blank=True)
    studio = models.CharField(max_length=100, blank=True)
    genre = models.CharField(max_length=200, blank=True)
    disc_count = models.IntegerField(default=1)
    movie_count = models.IntegerField(default=1)

    def __str__(self):
        return self.title_clean


class MovieUserList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="movieuserlist", null=True
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True)
    activated = models.BooleanField(default=True)
    rating = models.IntegerField(default=0)
    rented = models.BooleanField(default=False)
    rented_to = models.CharField(max_length=100, blank=True)
    date_added = models.DateField(auto_now_add=True, null=True)
