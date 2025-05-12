from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from mongoengine.queryset.visitor import Q
from .consumers import Message

class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
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
