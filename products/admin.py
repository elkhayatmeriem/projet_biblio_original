from django.contrib import admin
from .models import Category, Book
from accounts.models import Borrow


# CATEGORY
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


# BOOK
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'available')
    list_filter = ('category', 'available')
    search_fields = ('title', 'author', 'description')
    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrowed_at', 'returned')
    list_filter = ('borrowed_at',)
    search_fields = ('user__username', 'book__title')