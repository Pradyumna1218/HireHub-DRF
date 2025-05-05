from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, Payment
from users.models import User
from django.conf import settings
import requests
from payments.serializers import PaymentSerializer
from django.utils import timezone

class PaymentCreateView(APIView):
    def post(self, request):
        user = request.user
        order_id = request.data.get("order_id")

        if not order_id:
            return Response(
                {"error": "order_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id = order_id, client__user=user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found for this user"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        existing_payment = Payment.objects.filter(order=order, status = "Pending").first()
        if existing_payment:
            serializer = PaymentSerializer(existing_payment)
            return Response(serializer.data,
                            status = status.HTTP_200_OK)
        
        payment = Payment.objects.create(
            order = order,
            user = user,
            payment_amount = order.total_amount,
            status = "Pending",
            payment_date = timezone.now()
        )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class KhaltiPaymentVerifyView(APIView):
    def post(self, request):
        token = request.data.get("token")
        order_id = request.data.get("order_id")
        amount = request.data.get("amount")

        if not all([token, order_id, amount]):
            return Response(
                {"error": "token, order_id, amount required"},
                status = status.HTTP_400_BAD_REQUEST
                )
        
        try:
            order = Order.objects.get(id = order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order Not Found"},
                status = status.HTTP_400_BAD_REQUEST
                )
        
        payment_qs = Payment.objects.filter(
            order = order, 
            payment_amount = (int(amount) / 100)
        )
        payment = payment_qs.first()
        if not payment:
            return Response({
                "error": "Payment record not found for this order and amount."}, 
                status=404
            )
        
        url = "https://khalti.com/api/v2/payment/verify"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": f"key {settings.KHALTI_SECRET_KEY}"
        }

        response = requests.post(url, data = payload, headers = headers)
        khalti_response = response.json()

        if response.status_code == 200:
            payment.status = "Completed"
            payment.khalti_token = token
            payment.khalti_transaction_id = khalti_response.get("idx")
            payment.is_verified = True
            payment.save()

            return Response(
                {"message": "Payment verified successfully"}
            )
        else:
            return Response({
                "error": "Khalti verification failed.",
                "details": khalti_response
            }, status=status.HTTP_400_BAD_REQUEST)

