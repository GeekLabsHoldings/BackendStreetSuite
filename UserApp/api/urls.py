from rest_framework.authtoken.views import obtain_auth_token
from UserApp.api.views import (logout, ProfileView ,change_password,profileSettingsView ,ResetPasswordView,
                                 SignUpView ,VerificationView, log_in , ForgetPassword , VerifyForgetPasswordView , google_login)
from django.urls import path, include
from rest_framework_simplejwt.views import TokenBlacklistView , TokenObtainPairView, TokenRefreshView

urlpatterns = [

    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('login/', log_in, name='login'),
    path('google/login/', google_login, name='google-login'),
    path('register/', SignUpView.as_view(), name='register'),
    path('signup/verify/', VerificationView.as_view(), name='verify'),
    path('setpassword/', ResetPasswordView.as_view(), name='setpassword'),
    path('forgetpassword/', ForgetPassword.as_view(), name='forgetpassword'),
    path('forgetpassword/verify/', VerifyForgetPasswordView.as_view(), name='forgetpassword-verify'),
    path('forgetpassword/reset/', ResetPasswordView.as_view(), name='forgetpassword-reset'),
    path('profile-settings/', profileSettingsView, name='profile-settings'),
    path('change-password/', change_password, name='change-password'),  
    path('logout/', logout, name='logout'),
    # ### for jwt ###
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]

    