from rest_framework import serializers
from payments.models import Order, Payment

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
    order = OrderSerializer()
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user', 'status', 'payment_amount', 'payment_date', 
            'khalti_token', 'khalti_transaction_id', 'is_verified'
        ]
