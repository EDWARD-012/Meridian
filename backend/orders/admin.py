from django.contrib import admin
from .models import Address, Order, OrderItem, Payment, OrderTracking


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "city", "user", "is_default")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "status", "order_date")
    list_filter = ("status",)
    inlines = [OrderItemInline, OrderTrackingInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "payment_method", "amount", "status", "transaction_id")


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "message", "location", "recorded_at")
