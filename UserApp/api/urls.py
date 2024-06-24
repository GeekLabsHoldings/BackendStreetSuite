from rest_framework.authtoken.views import obtain_auth_token
from UserApp.api.views import logout, RegistrationView, ProfileView , GoogleLogIn , GoogleRedirectURIView
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('', include('allauth.urls')),
    # path('', include('dj_rest_auth.urls')),
    path('profile/<int:pk>/', ProfileView, name='profile'),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),

    path('google/login/', GoogleLogIn.as_view(), name='google_login'),
    path('google/login/callback/', GoogleRedirectURIView.as_view(), name='google-auth'),
    
]

    #path('login/', obtain_auth_token, name='login'),
    #path('logout/', logout, name='logout'),
    #path('register/', RegistrationView, name='register'),
    