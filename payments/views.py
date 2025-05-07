from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, Payment
from users.models import User
from django.conf import settings
from payments.serializers import PaymentSerializer, OrderSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from services.permissions import IsClient, IsFreelancer 

class FreelancerOrderListView(APIView):
    permission_classes = [IsFreelancer]

    def get(self, request):
        freelancer = request.user.freelancer
        order = Order.objects.filter(
            freelancer = freelancer
        ).select_related("service", "client")

        serializer = OrderSerializer(order, many = True)
        return Response(serializer.data, status= status.HTTP_200_OK)
    
class ClientOrderListView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        client = request.user.client
        orders = Order.objects.filter(
            client=client
        ).select_related("freelancer", "service")

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user = request.user
        
        try: 
            order = Order.objects.get(id = order_id, client__user = user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found for this user"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if order.status != "In Progress":
            return Response(
                {"error": "Order must be approved (set to In Progress) before payment can be created."},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_payment = Payment.objects.filter(order=order, status = "Pending").first()
        if existing_payment:
            serializer = PaymentSerializer(existing_payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
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
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        token = request.data.get("token")
        amount = request.data.get("amount")

        if not all([token, amount]):
            return Response(
                {"error": "Token and amount are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try: 
            order = Order.objects.get(id = order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        payment = Payment.objects.filter(
            order=order,
            payment_amount=(int(amount) / 100)
        ).first()

        if not payment:
            return Response(
                {"error": "Payment record not found for this order and amount."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        url = "https://khalti.com/api/v2/payment/verify"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
        }

        response = request.post(url, data = payload, headers = headers)
        khalti_response = response.json()

        if response.status_code == 200:
            payment.status = "Completed"
            payment.khalti_token = token
            payment.khalti_transaction_id = khalti_response.get("idx")
            payment.is_verified = True
            payment.save()

            return Response({"message": "Payment verified successfully"})
        else:
            return Response(
                {"error": "Khalti verification failed", "details": khalti_response},
                status=status.HTTP_400_BAD_REQUEST
            )

@login_required
def khalti_test_view(request):
    return render(request, 'payments/khalti_test.html')
