from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission
# Create your models here.
class CustomUser(AbstractUser):
    phone= models.CharField(max_length=20, blank=True,verbose_name="Num")
    address= models.TextField(blank=True,verbose_name="Adresse")
    class Meta:
        verbose_name ='Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    #Redefinition des relations pour eviter les conflits
    groups = models.ManyToManyField(
        Group,
        related_name ="Customuser_groups",
        related_query_name="user",
        blank=True,
        verbose_name='groups',
        help_text='the groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="Customuser_permissions",
        related_query_name= "user",
        blank= True,
        verbose_name='user permissions',
        help_text='Specific permissons for the user.'
    )