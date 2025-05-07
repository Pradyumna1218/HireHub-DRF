from django.urls import path
from .views import (
    FreelancerOrderListView,
    ClientOrderListView,
    PaymentCreateView, 
    KhaltiPaymentVerifyView, 
    khalti_test_view
)
urlpatterns = [
    path('orders/freelancer/', FreelancerOrderListView.as_view(), name='freelancer-orders'),
    path('orders/client/', ClientOrderListView.as_view(), name='client-orders'),
    path("payment/create/<int:order_id>/", PaymentCreateView.as_view(), name="create-payment"),
    path("khalti/verify/<int:order_id>/", KhaltiPaymentVerifyView.as_view(), name="khalti-verify"),
    path('test-khalti/', khalti_test_view, name='khalti-test'),

]
