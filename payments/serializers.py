from rest_framework import serializers
from .models import Order, Payment
from django.utils import timezone
from datetime import datetime
from django.utils import timezone


class OrderSerializer(serializers.ModelSerializer):
    delivery_time = serializers.CharField(write_only=True, required=False)
    client_name = serializers.SerializerMethodField()
    order_date = serializers.SerializerMethodField()
    delivery_date = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'client_name', 'service', 'order_date', 
            'delivery_date', 'total_amount', 'status', 'delivery_time'
        ]
        read_only_fields = ['order_date', 'delivery_date', 'status']

    def get_client_name(self, obj):
        return obj.client.get_full_name() if hasattr(obj.client, 'get_full_name') else str(obj.client)

    def get_order_date(self, obj):
        return obj.order_date.strftime("%d %b, %H:%M, %Y")  # e.g., "02 May, 10:45, 2025"

    def get_delivery_date(self, obj):
        return obj.delivery_date.strftime("%d %b, %H:%M, %Y")

    def create(self, validated_data):
        delivery_time_str = validated_data.pop('delivery_time', None)
        if delivery_time_str:
            validated_data['delivery_date'] = self.parse_delivery_time(delivery_time_str)
        else:
            raise serializers.ValidationError({"delivery_time": "This field is required."})

        validated_data['order_date'] = timezone.now()
        validated_data['status'] = "Pending"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        delivery_time_str = validated_data.pop('delivery_time', None)
        if delivery_time_str:
            instance.delivery_date = self.parse_delivery_time(delivery_time_str)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def parse_delivery_time(self, time_str):
        from django.utils import timezone
        current_year = timezone.now().year
        try:
            return datetime.strptime(f"{current_year}-{time_str}", "%Y-%d-%m %H:%M")
        except ValueError:
            raise serializers.ValidationError({
                "delivery_time": "Expected format 'DD-MM HH:MM', e.g. '12-05 15:30'"
            })




class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user',
            'payment_amount', 'payment_date', 'status'
        ]
        read_only_fields = ['id', 'payment_date']
