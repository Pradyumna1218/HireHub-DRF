from channels.generic.websocket import AsyncConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
import json
from .models import Message

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
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
        self.room_group_name = f'chat_{self.sender.username}_{self.receiver}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.send({'type': 'websocket.accept'})

    async def websocket_disconnect(self, event):
        if self.room_group_name:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def websocket_receive(self, event):
        data = json.loads(event['text'])
        message = data['message']

        await self.save_message(self.sender.username, self.receiver, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message
            }
        )

    async def chat_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps({
                'message': event['message']
            })
        })

    @database_sync_to_async
    def save_message(self, sender_username, receiver_username, message):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=receiver_username)

        Message(
            sender_id=str(sender.id),
            receiver_id=str(receiver.id),
            message=message
        ).save()
