from rest_framework.authtoken.views import obtain_auth_token
from UserApp.api.views import logout, ProfileView , GoogleLogIn , GoogleRedirectURIView ,SignUpView ,VerificationView, log_in , RegistrationView, ForgetPassword
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
    