
from mongoengine import Document, StringField, DateTimeField
from django.utils import timezone
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


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


class Review(models.Model):
    freelancer = models.ForeignKey("users.freelancer", on_delete=models.CASCADE, related_name="reviews")
    client = models.ForeignKey("users.client", on_delete=models.CASCADE, related_name="reviews")
    message = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['client', 'freelancer']


