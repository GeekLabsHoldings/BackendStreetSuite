from rest_framework.authtoken.views import obtain_auth_token
from UserApp.api.views import logout, RegistrationView, ProfileView
from django.urls import path

urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('register/', RegistrationView, name='register'),
    path('logout/', logout, name='logout'),
    path('profile/<int:pk>/', ProfileView, name='profile')
    
]
