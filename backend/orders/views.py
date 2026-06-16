import uuid
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView
from django.shortcuts import get_object_or_404
from catalog.models import Product
from cart.models import Cart
from .models import Address, Order, OrderItem, Payment, OrderTracking
from .serializers import (
    AddressSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    PlaceOrderSerializer,
)


TRACKING_MESSAGES = {
    Order.Status.PENDING: "Order placed successfully",
    Order.Status.CONFIRMED: "Order confirmed by seller",
    Order.Status.PROCESSING: "Order is being packed",
    Order.Status.SHIPPED: "Order shipped from warehouse",
    Order.Status.OUT_FOR_DELIVERY: "Out for delivery in your area",
    Order.Status.DELIVERED: "Order delivered successfully",
    Order.Status.CANCELLED: "Order cancelled",
}


class AddressListCreateView(ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if serializer.validated_data.get("is_default"):
            Address.objects.filter(user=self.request.user).update(is_default=False)
        serializer.save(user=self.request.user)


class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        address = get_object_or_404(Address, pk=data["address_id"], user=request.user)
        cart = get_object_or_404(
            Cart.objects.prefetch_related("items__product"),
            user=request.user,
        )
        cart_items = list(cart.items.all())
        if not cart_items:
            return Response({"detail": "Cart is empty."}, status=400)

        for item in cart_items:
            product = Product.objects.select_for_update().get(pk=item.product_id)
            if item.quantity > product.stock_quantity:
                return Response(
                    {"detail": f"Insufficient stock for {product.name}."},
                    status=400,
                )

        total = sum(item.line_total for item in cart_items)
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total,
            status=Order.Status.PENDING,
        )

        for item in cart_items:
            product = Product.objects.select_for_update().get(pk=item.product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=product.price * item.quantity,
            )
            product.stock_quantity -= item.quantity
            product.save(update_fields=["stock_quantity"])

        payment_status = (
            Payment.Status.SUCCESS
            if data["payment_method"] != "cod"
            else Payment.Status.PENDING
        )
        txn_id = (
            f"TXN-{uuid.uuid4().hex[:12].upper()}"
            if payment_status == Payment.Status.SUCCESS
            else ""
        )
        paid_at = timezone.now() if payment_status == Payment.Status.SUCCESS else None

        Payment.objects.create(
            order=order,
            payment_method=data["payment_method"],
            amount=total,
            status=payment_status,
            transaction_id=txn_id,
            paid_at=paid_at,
        )

        OrderTracking.objects.create(
            order=order,
            status=Order.Status.PENDING,
            message=TRACKING_MESSAGES[Order.Status.PENDING],
            location=address.city,
        )
        if payment_status == Payment.Status.SUCCESS:
            order.status = Order.Status.CONFIRMED
            order.save(update_fields=["status"])
            OrderTracking.objects.create(
                order=order,
                status=Order.Status.CONFIRMED,
                message=TRACKING_MESSAGES[Order.Status.CONFIRMED],
                location="Warehouse",
            )

        cart.items.all().delete()
        order = Order.objects.prefetch_related(
            "items__product__category", "payment", "tracking_events", "address"
        ).get(pk=order.pk)
        return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("payment")


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items__product__category", "payment", "tracking_events", "address"
        )


class OrderTrackView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "tracking_events", "items__product", "payment", "address"
        )

    lookup_url_kwarg = "order_id"
