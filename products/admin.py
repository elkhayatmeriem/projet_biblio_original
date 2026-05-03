from django.contrib import admin
from .models import Category, Book, Borrow


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


# BORROW
@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'borrow_date', 'return_date')
    list_filter = ('borrow_date',)
    search_fields = ('student',)