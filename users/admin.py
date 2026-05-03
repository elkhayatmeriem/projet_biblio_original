from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ('Information supplementaire', {
            'fields': ('phone', 'address')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Information supplementaire', {
            'fields': ('username', 'email', 'phone', 'address')
        }),
    )

    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active')