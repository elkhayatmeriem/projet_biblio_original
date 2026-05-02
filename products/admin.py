from django.contrib import admin
from .models import Category, Book, Borrow


# Category admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


# Book admin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'available')
    list_filter = ('category', 'available')
    search_fields = ('title', 'author', 'description')


# Borrow admin
@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'borrow_date', 'return_date')
    list_filter = ('borrow_date',)
    search_fields = ('student',)