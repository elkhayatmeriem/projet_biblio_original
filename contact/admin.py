from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'email', 'message', 'date_envoi')
    readonly_fields = ('nom', 'email', 'message', 'date_envoi')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False