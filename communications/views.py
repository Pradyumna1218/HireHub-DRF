from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from mongoengine.queryset.visitor import Q
from .consumers import Message
from .serializers import ReviewSerialzer
from services.permissions import IsClient
from rest_framework import status
from .models import Review
from payments.models import Payment, Order 
from django.db.models import Avg

class ChatHistoryView(APIView):
    """
    API endpoint to retrieve the chat history between the authenticated user
    and another user specified by username.

    Permissions:
        - Requires authentication.

    Methods:
        - GET: Returns all messages exchanged between the logged-in user and the target user,
               ordered by timestamp.
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        """
        Handle GET request to retrieve chat history with a specific user.

        Args:
            request (HttpRequest): The request object containing the authenticated user.
            username (str): The username of the user to retrieve chat history with.

        Returns:
            Response: A list of messages (as dictionaries) between the authenticated user and the target user.
        """

        User = get_user_model()
        sender = request.user
        receiver = get_object_or_404(User, username=username)

        messages = Message.objects.filter(
            Q(sender_id=str(sender.id), receiver_id=str(receiver.id)) |
            Q(sender_id=str(receiver.id), receiver_id=str(sender.id))
        ).order_by('timestamp')

        data = [
            {
                'sender_id': msg.sender_id,
                'receiver_id': msg.receiver_id,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        return Response(data)
    
class ReviewCreateView(APIView):
    permission_classes = [IsClient]

    def post(self, request, order_id):
        client = request.user.client        
        order = get_object_or_404(
            Order.objects.all().select_related(
                "freelancer",
                "freelancer__user"
            ), 
            id=order_id
        )

        payment_qs = Payment.objects.filter(
            order=order,
            user=request.user,  
            status='Completed'  
        )

        if not payment_qs.exists():
            return Response(
                {"error": "Can't review a freelancer without completed payment."},
                status=status.HTTP_403_FORBIDDEN
            )

        freelancer = order.freelancer
        data = request.data.copy()
        data['freelancer'] = freelancer.user.id 
        data['client'] = client.user.id          

        existing_review = Review.objects.select_related(
            'freelancer', 
            'freelancer__user', 
            'client', 
            'client__user'
        ).filter(
            client=client, 
            freelancer=freelancer
        ).first()

        if existing_review:
            serializer = ReviewSerialzer(existing_review, data=data, partial=True)
        else:
            serializer = ReviewSerialzer(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save(client=client, freelancer=freelancer)

        avg_rating = Review.objects.filter(
            freelancer=freelancer
        ).aggregate(avg=Avg('rating'))['avg'] or 0.0

        freelancer.rating = round(avg_rating, 1)
        freelancer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)