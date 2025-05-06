from rest_framework import serializers
from datetime import datetime
from django.utils import timezone
from payments.models import Order, Payment
from users.models import Client

class OrderSerializer(serializers.ModelSerializer):
    delivery_time = serializers.CharField(write_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'client_name', 'service', 'order_date', 
            'delivery_date', 'total_amount', 'status', 'delivery_time'
        ]
        read_only_fields = ['order_date', 'delivery_date', 'sta tus']

    def get_client_name(self, obj):
        return obj.client.user.username

    def validate(self, attrs):
        delivery_time_str = attrs.pop('delivery_time', None)
        if not delivery_time_str:
            raise serializers.ValidationError({"delivery_time": "This field is required."})

        current_year = timezone.now().year
        try:
            full_string = f"{current_year}-{delivery_time_str}"  
            parsed_dt = datetime.strptime(full_string, "%Y-%m-%d %H:%M")
            attrs['delivery_date'] = timezone.make_aware(parsed_dt)
        except ValueError:
            raise serializers.ValidationError({
                "delivery_time": "Expected format 'MM-DD HH:MM', e.g. '05-12 15:30'"
            })

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        service = validated_data.pop('service')

        try:
            client = user.client
        except Client.DoesNotExist:
            raise serializers.ValidationError("Client not found.")

        return Order.objects.create(
            client=client,
            service=service,
            order_date=timezone.now(),
            status='Pending',
            **validated_data
        )


        

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
