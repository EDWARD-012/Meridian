from rest_framework import serializers
from catalog.serializers import ProductListSerializer
from .models import Address, Order, OrderItem, Payment, OrderTracking


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id", "full_name", "line1", "city", "state",
            "pincode", "is_default", "created_at",
        )
        read_only_fields = ("created_at",)


class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ("id", "status", "message", "location", "recorded_at")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id", "payment_method", "amount", "status",
            "transaction_id", "paid_at",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "unit_price", "subtotal")


class OrderListSerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(source="items.count", read_only=True)
    payment_status = serializers.CharField(source="payment.status", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "total_amount", "status", "order_date",
            "item_count", "payment_status",
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    tracking_events = OrderTrackingSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "total_amount", "status", "order_date", "updated_at",
            "address", "items", "payment", "tracking_events",
        )


class PlaceOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.Method.choices, default="cod")
