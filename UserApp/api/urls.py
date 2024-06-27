from rest_framework.authtoken.views import obtain_auth_token
<<<<<<< HEAD
from UserApp.api.views import logout, ProfileView , GoogleLogIn , GoogleRedirectURIView ,SignUpView ,VerificationView, log_in  , ForgetPassword
=======
from UserApp.api.views import logout, ProfileView , GoogleLogIn , GoogleRedirectURIView ,SignUpView ,VerificationView, log_in , RegistrationView
>>>>>>> 0bf24a8b29266ac56869a3a6f44c2cecddec59b5
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [

    path('profile/<int:pk>/', ProfileView, name='profile'),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),

    path('google-signup/', GoogleLogIn.as_view(), name='google_signup'),
    path('google-login/', GoogleLogIn.as_view(), name='google_login'),
    path('google/login/callback/', GoogleRedirectURIView.as_view(), name='google-auth'),
    path('login/', log_in, name='login'),
    path('register/', SignUpView.as_view(), name='register'),
    path('signup/verify/', VerificationView.as_view(), name='verify'),
    path('forgetpassword/', ForgetPassword.as_view(), name='forgetpassword'),
    
]

    #path('logout/', logout, name='logout'),
    