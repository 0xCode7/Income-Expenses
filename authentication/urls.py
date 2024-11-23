from tkinter.font import names

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import *


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),

    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('activate/<uidb64>/<token>', ActivateAccountView.as_view(), name='activate'),
    path('reset-user-password/<uidb64>/<token>', CompletePasswordReset.as_view(), name='reset-user-password'),

    path('request-reset-link/', ResetPasswordView.as_view(), name='request-reset-link'),

    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
