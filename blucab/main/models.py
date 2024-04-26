from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ToDoList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="todolist", null=True)
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
    release = models.CharField(max_length=4)
    runtime = models.CharField(max_length=5)
    fsk = models.CharField(max_length=50)
    content = models.CharField(max_length=10000)
    actor = models.CharField(max_length=500)
    regisseur = models.CharField(max_length=100)
    studio = models.CharField(max_length=100)

    def __str__(self):
        return self.title_clean

