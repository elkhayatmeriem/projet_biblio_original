from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    # ✅ FIXED: use custom user model correctly
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200)
    author = models.TextField()

    isbn = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    description = models.TextField(null=True, blank=True)

    image_url = models.URLField(null=True, blank=True)

    image = models.ImageField(
        upload_to='books/',
        null=True,
        blank=True
    )

    available = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Borrow(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    student = models.CharField(max_length=200)

    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.student} -> {self.book.title}"