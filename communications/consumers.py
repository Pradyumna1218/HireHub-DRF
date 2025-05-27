from channels.generic.websocket import AsyncConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
import json
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncConsumer):
    """
    WebSocket consumer that handles real-time chat functionality between authenticated users.

    Responsibilities:
    - Authenticates users via JWT passed in headers.
    - Assigns users to a consistent chat room group based on sorted usernames.
    - Broadcasts messages between participants in the same room.
    - Persists chat messages to the database.
    """

    async def websocket_connect(self, event):
        """
        Handles WebSocket connection initiation.

        Steps:
        - Authenticates user via JWT token from headers.
        - Extracts the receiver's username from the URL.
        - Constructs a unique and deterministic room group name.
        - Joins the user to the appropriate channel group.
        """
         
        self.room_group_name = None

        try:
            headers = dict(self.scope["headers"])
            auth_header = headers.get(b'authorization', b'').decode()

            if not auth_header.startswith('Bearer '):
                print("[AUTH ERROR] Invalid header format.")
                await self.send({'type': 'websocket.close'})
                return

            token = auth_header.split()[1]
            access_token = AccessToken(token)
            user_id = access_token['user_id']

            self.sender = await database_sync_to_async(User.objects.get)(id=user_id)
            print(f"[AUTH SUCCESS] Sender: {self.sender.username}")

        except Exception as e:
            print(f"[AUTH FAILED] Reason: {str(e)}")
            await self.send({'type': 'websocket.close'})
            return

        try:
            self.receiver = self.scope['url_route']['kwargs']['username']
            usernames = sorted([self.sender.username, self.receiver])
            self.room_group_name = f"chat_{usernames[0]}_{usernames[1]}"

            print(f"[CONNECTED] Sender: {self.sender.username}, Receiver: {self.receiver}")
            print(f"[ROOM CREATED] Room Group: {self.room_group_name}")

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.send({'type': 'websocket.accept'})

        except Exception as e:
            print(f"[ERROR CONNECTING TO GROUP] {str(e)}")
            await self.send({'type': 'websocket.close'})

    async def websocket_disconnect(self, event):
        """
        Handles cleanup on WebSocket disconnection.

        Removes the current user from the room group if it was created.
        """

        if hasattr(self, 'room_group_name'):
            print(f"[DISCONNECT] Leaving group: {self.room_group_name}")
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def websocket_receive(self, event):
        """
        Handles an incoming WebSocket message.

        - Parses the JSON message.
        - Saves it to the database.
        - Broadcasts it to all users in the room group.
        """

        try:
            data = json.loads(event['text'])
            message = data['message']

            print(f"[RECEIVED] Message: {message} from {self.sender.username} to {self.receiver}")
            print(f"[BROADCAST] To group: {self.room_group_name}")

            await self.save_message(self.sender.username, self.receiver, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )
        except Exception as e:
            print(f"[ERROR RECEIVING MESSAGE] {str(e)}")

    async def chat_message(self, event):
        """
        Receives a broadcast message from the room group and sends it to the WebSocket client.

        Expects:
            event = {
                'type': 'chat_message',
                'message': <str>
            }
        """

        try:
            print(f"[GROUP MESSAGE] Dispatching: {event['message']}")
            await self.send({
                'type': 'websocket.send',
                'text': json.dumps({
                    'message': event['message']
                })
            })
        except Exception as e:
            print(f"[ERROR SENDING MESSAGE] {str(e)}")

    @database_sync_to_async
    def save_message(self, sender_username, receiver_username, message):
        """
        Persists the chat message to the database.

        Args:
            sender_username (str): The username of the sender.
            receiver_username (str): The username of the receiver.
            message (str): The message content.
        """
        
        try:
            sender = User.objects.get(username=sender_username)
            receiver = User.objects.get(username=receiver_username)

            Message.objects.create(
                sender_id=str(sender.id),
                receiver_id=str(receiver.id),
                message=message
            )
            print(f"[DB SAVE] Message saved from {sender.username} to {receiver.username}")

        except Exception as e:
            print(f"[DB ERROR] {str(e)}")
