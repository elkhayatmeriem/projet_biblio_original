from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # IMPORTANT: on utilise item_id (PAS book_id)
    path('emprunter/<int:item_id>/', views.emprunter, name='emprunter'),

    path('retourner/<int:borrow_id>/', views.retourner, name='retourner'),
]