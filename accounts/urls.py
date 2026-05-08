from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [

    # AUTH
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # USER FEATURES
    path('emprunts/', views.emprunts, name='emprunts'),
    path('penalites/', views.penalites, name='penalites'),
    path('mes-informations/', views.my_information, name='my_information'),
    path('edit/', views.edit_information, name='edit_information'),
    path('change-password/', views.change_password, name='change_password'),

]