from django.db import models
from django.contrib.auth.models import User
from products.models import Book
from django.utils import timezone
from datetime import timedelta


class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    blocked_days = models.IntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)
    sanction_applied = models.BooleanField(default=False)

    notification = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    @property
    def due_date(self):
        return self.borrowed_at + timedelta(days=7)

    def is_late(self):
        check_date = self.returned_at if self.returned_at else timezone.now()
        return check_date > self.due_date

    def __str__(self):
        if self.book:
            return f"{self.user.username} - {self.book.title}"
        return f"{self.user.username} - Livre supprimé"