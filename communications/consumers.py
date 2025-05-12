import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime
from mongoengine import Document, StringField, DateTimeField


# ✅ This is fine at the top because it's mongoengine (not Django ORM)
class Message(Document):
    sender_id = StringField(required=True)
    receiver_id = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'chat_messages',
        'ordering': ['-timestamp']
    }


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            headers = dict(self.scope["headers"])
            auth_header = headers.get(b'authorization', b'').decode()

            if not auth_header.startswith('Bearer '):
                await self.close()
                return

            token = auth_header.split()[1]
            access_token = AccessToken(token)
            user_id = access_token['user_id']

            # ✅ Do NOT import User at the top, import inside the function
            from django.contrib.auth import get_user_model
            User = get_user_model()

            self.sender = await database_sync_to_async(User.objects.get)(id=user_id)
        except Exception as e:
            await self.close()
            return

        self.receiver = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'chat_{self.sender.username}_{self.receiver}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
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
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, sender_username, receiver_username, message):
        # ✅ Import only when needed
        from django.contrib.auth import get_user_model
        User = get_user_model()

        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=receiver_username)

        Message(
            sender_id=str(sender.id),
            receiver_id=str(receiver.id),
            message=message
        ).save()
