
from mongoengine import Document, StringField, DateTimeField
from django.utils import timezone

class Message(Document):
    """
    MongoDB document representing a chat message between two users.

    Fields:
        sender_id (str): ID of the user sending the message.
        receiver_id (str): ID of the user receiving the message.
        message (str): The content of the message.
        timestamp (datetime): The time the message was sent (defaults to now).

    Meta:
        collection (str): Specifies the MongoDB collection name as 'chat_messages'.
        ordering (list): Orders query results by descending timestamp.
    """
    
    sender_id = StringField(required=True)
    receiver_id = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'chat_messages',
        'ordering': ['-timestamp']
    }
