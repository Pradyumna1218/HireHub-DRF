from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .mongo import save_messages, get_messages
from .permissions import IsClientOrFreelancer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

User = get_user_model()


class SendMessageView(APIView):
    permission_classes = [IsClientOrFreelancer] 

    def post(self, request):
        sender_id = str(request.user.id)
        receiver_username = request.data.get("receiver")
        content = request.data.get("content")

        try:
            receiver = User.objects.get(username=receiver_username)
            receiver_id = str(receiver.id)
        except User.DoesNotExist:
            raise NotFound("Receiver not found")
        
        if sender_id == receiver_id:
            return Response(
                {"error": "You cannot send a message to yourself."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not all([sender_id, receiver_id, content]):
            return Response(
                {"error": "Missing fields"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        save_messages(sender_id, receiver_id, content)
        return Response(
            {"message": "Message sent"},
            status=status.HTTP_201_CREATED
        )
    

class ChatMessageView(APIView):
    permission_classes = [IsClientOrFreelancer] 

    def get(self, request, username):
        current_user_id = str(request.user.id)

        try:
            other_user = User.objects.get(username = username)
        except User.DoesNotExist:
            raise NotFound("User not found")
        
        other_user_id = str(other_user.id)

        if current_user_id == other_user_id:
            return Response(
                {"error": "You cannot view a chat with yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        messages = get_messages(current_user_id, other_user_id)

        messages_to_return = [
            msg for msg in messages
            if msg['sender_id'] == current_user_id
            or msg['receiver_id'] == current_user_id
        ]

        if not messages_to_return:
            return Response(
                {"message": "Start A New Conversation"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        for msg in messages_to_return:
            msg["_id"] = str(msg["_id"])
            msg["timestamp"] = msg["timestamp"].isoformat()

        return Response(messages_to_return, status=status.HTTP_200_OK)
        
            
