import uuid
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from catalog.models import Product
from cart.models import Cart, CartItem
from cart.services import get_or_create_cart
from .models import Order, OrderItem, Payment, OrderTracking, Address


TRACKING_MESSAGES = {
    Order.Status.PENDING: "Order placed successfully",
    Order.Status.CONFIRMED: "Order confirmed by seller",
    Order.Status.PROCESSING: "Order is being packed",
    Order.Status.SHIPPED: "Order shipped from warehouse",
    Order.Status.OUT_FOR_DELIVERY: "Out for delivery in your area",
    Order.Status.DELIVERED: "Order delivered successfully",
    Order.Status.CANCELLED: "Order cancelled",
}


def clear_cart_for_order(user, order):
    """Remove order line quantities from the user's cart (after successful payment)."""
    cart = get_or_create_cart(user)
    order_qty = {item.product_id: item.quantity for item in order.items.all()}
    for cart_item in cart.items.filter(product_id__in=order_qty):
        remove_qty = order_qty[cart_item.product_id]
        if cart_item.quantity <= remove_qty:
            cart_item.delete()
        else:
            cart_item.quantity -= remove_qty
            cart_item.save(update_fields=["quantity"])


@transaction.atomic
def place_order(user, address, payment_method):
    cart = get_object_or_404(Cart.objects.select_for_update(), user=user)
    cart_items = list(
        CartItem.objects.select_for_update()
        .filter(cart=cart)
        .select_related("product")
    )
    if not cart_items:
        raise ValueError("Your cart is empty.")

    product_ids = [item.product_id for item in cart_items]
    products = {
        p.id: p
        for p in Product.objects.select_for_update().filter(id__in=product_ids)
    }

    total = Decimal("0.00")
    for item in cart_items:
        product = products[item.product_id]
        if not product.is_active:
            raise ValueError(f"{product.name} is no longer available.")
        if item.quantity > product.stock_quantity:
            raise ValueError(f"Insufficient stock for {product.name}.")
        total += product.price * item.quantity

    order = Order.objects.create(
        user=user,
        address=address,
        total_amount=total,
        status=Order.Status.PENDING,
    )

    for item in cart_items:
        product = products[item.product_id]
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            unit_price=product.price,
            subtotal=product.price * item.quantity,
        )
        product.stock_quantity -= item.quantity
        product.save(update_fields=["stock_quantity"])

    payment_status = Payment.Status.PENDING
    Payment.objects.create(
        order=order,
        payment_method=payment_method,
        amount=total,
        status=payment_status,
    )

    OrderTracking.objects.create(
        order=order,
        status=Order.Status.PENDING,
        message=TRACKING_MESSAGES[Order.Status.PENDING],
        location=address.city,
    )

    if payment_method == Payment.Method.COD:
        order.status = Order.Status.CONFIRMED
        order.save(update_fields=["status", "updated_at"])
        OrderTracking.objects.create(
            order=order,
            status=Order.Status.CONFIRMED,
            message=TRACKING_MESSAGES[Order.Status.CONFIRMED],
            location="Warehouse",
        )

    if payment_method != Payment.Method.RAZORPAY:
        cart.items.all().delete()
    return order


@transaction.atomic
def fail_razorpay_payment(order):
    """Cancel unpaid Razorpay order and restore inventory."""
    order = Order.objects.select_for_update().get(pk=order.pk)
    payment = Payment.objects.select_for_update().get(order=order)

    if payment.status == Payment.Status.SUCCESS:
        return payment
    if payment.status == Payment.Status.FAILED:
        return payment

    product_ids = list(order.items.values_list("product_id", flat=True))
    products = {
        p.id: p
        for p in Product.objects.select_for_update().filter(id__in=product_ids)
    }
    for item in order.items.select_related("product"):
        product = products[item.product_id]
        product.stock_quantity += item.quantity
        product.save(update_fields=["stock_quantity"])

    payment.status = Payment.Status.FAILED
    payment.save(update_fields=["status"])

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    OrderTracking.objects.create(
        order=order,
        status=Order.Status.CANCELLED,
        message=TRACKING_MESSAGES[Order.Status.CANCELLED],
        location="Payment gateway",
    )
    return payment


@transaction.atomic
def cancel_stale_razorpay_order(order):
    """Cancel unpaid Razorpay order and restore stock (idempotent)."""
    order = Order.objects.select_for_update().get(pk=order.pk)
    payment = Payment.objects.select_for_update().get(order=order)

    if payment.payment_method != Payment.Method.RAZORPAY:
        return False
    if payment.status != Payment.Status.PENDING:
        return False
    if order.status == Order.Status.CANCELLED:
        return False

    product_ids = list(order.items.values_list("product_id", flat=True))
    products = {
        p.id: p
        for p in Product.objects.select_for_update().filter(id__in=product_ids)
    }
    for item in order.items.select_related("product"):
        product = products[item.product_id]
        product.stock_quantity += item.quantity
        product.save(update_fields=["stock_quantity"])

    payment.status = Payment.Status.FAILED
    payment.save(update_fields=["status"])
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    OrderTracking.objects.create(
        order=order,
        status=Order.Status.CANCELLED,
        message="Order auto-cancelled — payment not completed in time",
        location="System",
    )
    return True


@transaction.atomic
def confirm_razorpay_payment(order):
    """Mark Razorpay payment successful (demo gateway). Idempotent."""
    order = Order.objects.select_for_update().get(pk=order.pk)
    payment = Payment.objects.select_for_update().get(order=order)

    if payment.status == Payment.Status.SUCCESS:
        return payment
    if payment.status == Payment.Status.FAILED:
        raise ValueError("This order was cancelled after payment failure.")

    payment.status = Payment.Status.SUCCESS
    if not payment.transaction_id:
        payment.transaction_id = f"pay_{uuid.uuid4().hex[:16]}"
    payment.paid_at = timezone.now()
    payment.save(update_fields=["status", "transaction_id", "paid_at"])

    if order.status == Order.Status.PENDING:
        order.status = Order.Status.CONFIRMED
        order.save(update_fields=["status", "updated_at"])
        OrderTracking.objects.create(
            order=order,
            status=Order.Status.CONFIRMED,
            message=TRACKING_MESSAGES[Order.Status.CONFIRMED],
            location="Razorpay Gateway",
        )
    clear_cart_for_order(order.user, order)
    return payment
