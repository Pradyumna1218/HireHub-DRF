from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("Connection Created.....", event)
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        print("Message Received...", event)
        print(event['text'])
        await self.send({
            "type": "websocket.send",
            "text": "Message Sent By Client"
        })

    async def websocket_disconnect(self, event):
        print("Disconnected...", event)
        raise StopConsumer()
