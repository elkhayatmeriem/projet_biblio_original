from django.urls import path
from .views import BookList, BookDetail, ExternalBookDetail, search_books

urlpatterns = [
    path('', BookList.as_view(), name='books'),
    path('<int:pk>/', BookDetail.as_view(), name='book_detail'),
    path('external/<str:isbn>/', ExternalBookDetail.as_view(), name='external_book_detail'),
    path('search/', search_books, name='search_books'),
]