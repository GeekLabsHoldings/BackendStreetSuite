from rest_framework.authtoken.views import obtain_auth_token
from UserApp.api.views import logout, ProfileView , tokengetterview,GoogleLogIn,profileSettingsView ,ResetPasswordView, GoogleRedirectURIView ,SignUpView ,VerificationView, log_in , RegistrationView, ForgetPassword , VerifyForgetPasswordView
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [

    # path('profile/<int:pk>/', ProfileView, name='profile'),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),

    path('google-signup/', GoogleLogIn.as_view(), name='google_signup'),
    path('google-login/', GoogleLogIn.as_view(), name='google_login'),
    path('google/login/callback/', GoogleRedirectURIView.as_view(), name='google-callback'),
    # path('profile-settings/', GoogleRedirectURIView.as_view(), name='google-callback'),
    path('login/', log_in, name='login'),
    path('token/<str:email>/', tokengetterview, name='tokengetterview'),
    path('register/', SignUpView.as_view(), name='register'),
    path('signup/verify/', VerificationView.as_view(), name='verify'),
    path('setpassword/', ResetPasswordView.as_view(), name='setpassword'),
    path('forgetpassword/', ForgetPassword.as_view(), name='forgetpassword'),
    path('forgetpassword/verify/', VerifyForgetPasswordView.as_view(), name='forgetpassword-verify'),
    path('forgetpassword/reset/', ResetPasswordView.as_view(), name='forgetpassword-reset'),
    path('profile-settings/', profileSettingsView, name='profile-settings'), 
    
]

    #path('logout/', logout, name='logout'),
    