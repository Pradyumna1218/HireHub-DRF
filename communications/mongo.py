from pymongo import MongoClient
from django.conf import settings
from django.utils import timezone

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
chat_collection = db[settings.MONGO_CHAT_COLLECTION]

def save_messages(sender_id, receiver_id, content):
    chat_collection.insert_one({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "content": content,
        "timestamp": timezone.now(),
        "status": "sent"
    })

def get_messages(user1_id, user2_id):
    messages = chat_collection.find({
        "$or": [
            {"sender_id": user1_id, "receiver_id": user2_id},
            {"sender_id": user2_id, "receiver_id": user1_id},
        ],
    }).sort("timestamp", 1)
    return list(messages)

