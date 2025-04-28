from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenVerifyView,
)
from .views import(
    FreelancerRegisterView,
    ClientRegisterView,
    FreelancerProfileView,
    ClientProfileView,
    PasswordResetRequestView,
    PasswordResetView
)


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name = 'token-obtain-pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name = 'token-refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name = 'token-verify'),

    path('register/freelancer', FreelancerRegisterView.as_view(), name = 'freelancer-register'),
    path('register/client', ClientRegisterView.as_view(), name = 'client-register'),
    path('freelancer/profile/', FreelancerProfileView.as_view(), name='freelancer-profile'),
    path('client/profile/', ClientProfileView.as_view(), name='freelancer-profile'),
    path('request/', PasswordResetRequestView.as_view(), name='password-request'),
    path('reset/', PasswordResetView.as_view(), name='password-reset'),

]

