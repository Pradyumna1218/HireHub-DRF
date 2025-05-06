from django.urls import path
from .views import  ApproveOrderView, PaymentCreateView, KhaltiPaymentVerifyView, khalti_test_view

urlpatterns = [
    path("order/approve/<int:order_id>/", ApproveOrderView.as_view(), name="approve-order"),    
    path("payment/create/<int:order_id>/", PaymentCreateView.as_view(), name="create-payment"),
    path("khalti/verify/<int:order_id>/", KhaltiPaymentVerifyView.as_view(), name="khalti-verify"),
    path('test-khalti/', khalti_test_view, name='khalti-test'),

]
