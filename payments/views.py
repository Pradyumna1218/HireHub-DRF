from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from payments.models import Order
from .models import Payment
from django.conf import settings
from payments.serializers import PaymentSerializer, OrderSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from services.permissions import IsClient, IsFreelancer
import requests
from django.shortcuts import get_object_or_404

class FreelancerOrderListView(APIView):
    """
    GET: List all orders associated with the authenticated freelancer.
    Requires freelancer permissions.
    """

    permission_classes = [IsFreelancer]

    def get(self, request):
        freelancer = request.user.freelancer
        order = Order.objects.filter(
            freelancer=freelancer
        ).select_related(
            "service", 
            "client__user", 
            "freelancer__user"
        )

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ClientOrderListView(APIView):
    """
    GET: List all orders associated with the authenticated client.
    Requires client permissions.
    """

    permission_classes = [IsClient]

    def get(self, request):
        client = request.user.client
        orders = Order.objects.filter(
            client=client
        ).select_related("freelancer__user", "service", "client__user")

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class PaymentCreateView(APIView):
    """
    POST: Create a payment record and initiate Khalti payment for an order.
    If a pending payment exists, reuse it.
    Requires client permissions.
    """

    permission_classes = [IsClient]

    def post(self, request, order_id):
        user = request.user

        order = get_object_or_404(Order, id=order_id, client__user=user)

        existing_payment = Payment.objects.filter(order=order, status="Pending").first()
        if existing_payment:
            if not existing_payment.khalti_token:
                khalti_response = self.initiate_khalti_payment(order)
                if khalti_response:
                    existing_payment.khalti_token = khalti_response.get('pidx')
                    existing_payment.save()
                    serializer = PaymentSerializer(existing_payment)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"error": "Failed to initiate Khalti payment"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            serializer = PaymentSerializer(existing_payment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        payment = Payment.objects.create(
            order=order,
            user=user,
            status="Pending",
            payment_amount=order.total_amount,
            payment_date=timezone.now()
        )

        khalti_response = self.initiate_khalti_payment(order)
        if khalti_response:
            payment.khalti_token = khalti_response.get('pidx')
            payment.save()

            order.status = "In Progress"
            order.save()

            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            payment.delete()
            return Response(
                {"error": "Failed to initiate Khalti payment"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def initiate_khalti_payment(self, order):
        """
        Initiates a Khalti payment request for the given order.
        Returns the JSON response on success or None on failure.
        """

        url = "https://dev.khalti.com/api/v2/epayment/initiate/"
        payload = {
            "return_url": "http://example.com/",
            "website_url": "https://example.com/",
            "amount": int(order.total_amount * 100),
            "purchase_order_id": f"Order{order.id}",
            "purchase_order_name": "Freelancer Service Payment",
            "customer_info": {
                "name": order.client.user.username,
                "email": order.client.user.email or "test@khalti.com",
                "phone": order.client.user.phone or "9800000001"
            }
        }
        headers = {
            "Authorization": f"key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None


class KhaltiPaymentVerifyView(APIView):
    """
    POST: Verify Khalti payment using the payment token (pidx).
    Updates Payment and Order status accordingly.
    Requires authentication.
    """
    
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        pidx = request.data.get("token")

        if not pidx:
            return Response({"error": "Missing pidx (token)"}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, id=order_id)
        payment = get_object_or_404(Payment, order=order, khalti_token=pidx)

        url = "https://dev.khalti.com/api/v2/epayment/lookup/"
        payload = { "pidx": pidx }
        headers = {
            "Authorization": f"key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()

            if response.status_code == 200:
                payment.khalti_transaction_id = result.get("transaction_id")
                payment.is_verified = True
                payment.save()

                order.status = "Completed"
                order.save()

                return Response({"message": "Payment verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Verification failed", "details": result}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Connection error", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
