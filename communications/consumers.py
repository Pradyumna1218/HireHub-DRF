from channels.generic.websocket import AsyncConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
import json
from .models import Message

class ChatConsumer(AsyncConsumer):
    """
    WebSocket consumer for handling real-time chat between users.

    This consumer:
    - Authenticates users via JWT token from the 'Authorization' header.
    - Dynamically builds a chat room based on the sender and receiver's usernames.
    - Broadcasts messages to the appropriate room group.
    - Saves each chat message to the database.
    """

    async def websocket_connect(self, event):
        """
        Called when the WebSocket connection is initiated.

        - Authenticates the user using the JWT token from headers.
        - Extracts sender and receiver usernames.
        - Joins a unique room group for the chat session.
        """

        self.room_group_name = None  

        try:
            headers = dict(self.scope["headers"])
            auth_header = headers.get(b'authorization', b'').decode()

            if not auth_header.startswith('Bearer '):
                await self.send({'type': 'websocket.close'})
                return

            token = auth_header.split()[1]
            access_token = AccessToken(token)
            user_id = access_token['user_id']

            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.sender = await database_sync_to_async(User.objects.get)(id=user_id)

        except Exception as e:
            await self.send({'type': 'websocket.close'})
            return

        self.receiver = self.scope['url_route']['kwargs']['username']

        usernames = sorted([self.sender.username, self.receiver])
        self.room_group_name = f"chat_{usernames[0]}_{usernames[1]}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.send({'type': 'websocket.accept'})

    async def websocket_disconnect(self, event):
        """
        Called when the WebSocket connection is closed.

        - Removes the channel from the chat room group.
        """

        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def websocket_receive(self, event):
        """
        Called when a message is received from the WebSocket.

        - Parses the incoming message.
        - Saves it to the database.
        - Sends the message to all users in the room group.
        """

        data = json.loads(event['text'])
        message = data['message']

        await self.save_message(self.sender.username, self.receiver, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        """
        Handler for broadcast messages to the room group.

        - Sends the message to the WebSocket client.
        """
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps({
                'message': event['message']
            })
        })

    @database_sync_to_async
    def save_message(self, sender_username, receiver_username, message):
        """
        Persists the chat message to the database.

        Args:
            sender_username (str): Username of the message sender.
            receiver_username (str): Username of the message receiver.
            message (str): The chat message content.
        """
        
        from django.contrib.auth import get_user_model
        User = get_user_model()

        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=receiver_username)

        Message(
            sender_id=str(sender.id),
            receiver_id=str(receiver.id),
            message=message
        ).save()
