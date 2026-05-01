from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=200)
    author = models.TextField()
    isbn = models.CharField(max_length=50)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    available = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Borrow(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    student = models.CharField(max_length=200)

    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} -> {self.book.title}"
    
