from rest_framework import serializers
from datetime import datetime
from django.utils import timezone
from payments.models import Order, Payment
from users.models import Client

class OrderSerializer(serializers.ModelSerializer):
    freelancer = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            "id", "freelancer", "client", "delivery_date", 
            "total_amount", "service", "status" 
        ]

    def get_freelancer(self, obj):
        return obj.freelancer.user.username
    
    def get_client(self, obj):
        return obj.client.user.username
    
    def get_service(self, obj):
        return {
            "id": obj.service.id,
            "title": obj.service.title,
        }
       

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user','payment_amount', 
            'payment_date', 'status',"khalti_token", 
            "khalti_transaction_id", "is_verified"
        ]
        read_only_fields = ["payment_date", "is_verified", "status", "khalti_transaction_id"]

    def validate_payment_amount(self, value):
        
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        return value
