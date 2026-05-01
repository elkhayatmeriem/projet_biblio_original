from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('emprunts/', views.emprunts, name='emprunts'),
    path('penalites/', views.penalites, name='penalites'),
    path("mes-informations/", views.my_information, name="my_information"),
    path('change-password/', views.change_password, name='change_password'),
        path("edit/", views.edit_information, name="edit_information"),
]