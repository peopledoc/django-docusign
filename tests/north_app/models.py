from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)


class Book(models.Model):
    author = models.ForeignKey(Author)
    title = models.CharField(max_length=100)
    pages = models.IntegerField()
