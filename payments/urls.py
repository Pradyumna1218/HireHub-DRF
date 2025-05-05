from django.urls import path
from .views import KhaltiPaymentVerifyView, PaymentCreateView

urlpatterns = [
    path("payment/create/", PaymentCreateView.as_view(), name="create-payment"),
    path("khalti/verify/", KhaltiPaymentVerifyView.as_view(), name="khalti-verify"),
]
