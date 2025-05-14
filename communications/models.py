
from mongoengine import Document, StringField, DateTimeField
from django.utils import timezone

class Message(Document):
    sender_id = StringField(required=True)
    receiver_id = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'chat_messages',
        'ordering': ['-timestamp']
    }
