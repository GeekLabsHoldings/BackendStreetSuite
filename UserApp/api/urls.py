from rest_framework.authtoken.views import obtain_auth_token
from UserApp.api.views import logout, RegistrationView, ProfileView, GoogleLogin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', include('allauth.urls')),
    path('', include('dj_rest_auth.urls')),
    path('profile/<int:pk>/', ProfileView, name='profile'),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),

    path('google/login/', GoogleLogin.as_view(), name='google_login')
    
]

    #path('login/', obtain_auth_token, name='login'),
    #path('logout/', logout, name='logout'),
    #path('register/', RegistrationView, name='register'),
    