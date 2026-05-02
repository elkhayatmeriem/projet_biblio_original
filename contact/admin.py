from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'date_envoi','message')
    readonly_fields = ('nom', 'email', 'message', 'date_envoi')

    def has_change_permission(self, request, obj=None):
        return False  # empêche toute modification

    def has_add_permission(self, request):
        return False  # empêche ajout depuis admin

admin.site.register(Contact, ContactAdmin)