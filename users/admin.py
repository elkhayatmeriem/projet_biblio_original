from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# Register your models here.
@admin.register(CustomUser)
class CustomerAdmin(UserAdmin):
    #formulaire d'edition 
    fieldsets = UserAdmin.fieldsets + (
        ('Information supplementaire',{'fields': ('phone', 'address')}),
    )
    #formulaire d'ajout
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Information supplementaire',{'fields': ('email', 'phone', 'address')}),
    )