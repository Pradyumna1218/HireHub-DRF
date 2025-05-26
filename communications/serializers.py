from rest_framework import serializers
from .models import Review


class ReviewSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id', 'freelancer', 'client', 'message', 
            'rating', 'created_at'
        ]
        read_only_fields = ['client', 'created_at']
