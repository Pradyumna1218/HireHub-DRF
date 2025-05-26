from rest_framework import serializers
from payments.models import Order, Payment

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializes Order model with nested freelancer username, client username,
    and minimal service info (id and title).
    """

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
        """Return the username of the freelancer associated with the order."""
        return obj.freelancer.user.username
    
    def get_client(self, obj):
        """Return the username of the client associated with the order."""
        return obj.client.user.username
    
    def get_service(self, obj):
        """Return a dict with minimal service details: id and title."""
        return {
            "id": obj.service.id,
            "title": obj.service.title,
        }
       

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializes Payment model including nested OrderSerializer.
    Includes payment details and Khalti payment info.
    """
    
    order = OrderSerializer()
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user', 'status', 'payment_amount', 'payment_date', 
            'khalti_token', 'khalti_transaction_id', 'is_verified'
        ]
