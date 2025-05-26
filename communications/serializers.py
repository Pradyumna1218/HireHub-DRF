from rest_framework import serializers
from .models import Review


class ReviewSerialzer(serializers.ModelSerializer):
    freelancer = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = [
            'id', 'freelancer', 'client', 'message', 
            'rating', 'created_at'
        ]
        read_only_fields = ['id', 'client', 'created_at']

    def get_freelancer(self, obj):
        return obj.freelancer.user.username
    
    def get_client(self, obj):
        return obj.client.user.username