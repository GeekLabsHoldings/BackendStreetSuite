from UserApp.api.views import (logout ,change_password,profileSettingsView ,SignUpView,
                               VerificationView,log_in , ForgetPassword , VerifyForgetPasswordView , google_login , ResetForgetPasswordView)

from django.urls import path

urlpatterns = [
    path('login/', log_in, name='login'),
    path('google/login/', google_login, name='google-login'),
    path('register/', SignUpView.as_view(), name='register'),
    path('signup/verify/', VerificationView.as_view(), name='verify'),
    # path('setpassword/', ResetPasswordView.as_view(), name='setpassword'),
    path('forgetpassword/', ForgetPassword.as_view(), name='forgetpassword'),
    path('forgetpassword/verify/', VerifyForgetPasswordView.as_view(), name='forgetpassword-verify'),
    path('forgetpassword/reset/', ResetForgetPasswordView.as_view(), name='forgetpassword-reset'),
    # path('password-reset/', ResetPasswordView.as_view(), name='password-reset'),
    path('profile-settings/', profileSettingsView, name='profile-settings'),
    path('change-password/', change_password, name='change-password'),  
    path('logout/', logout, name='logout'),
]

    