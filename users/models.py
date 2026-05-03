from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name="Num")
    address = models.TextField(blank=True, verbose_name="Adresse")

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    # FIXED GROUPS
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )

    # FIXED PERMISSIONS
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set",
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for the user.'
    )