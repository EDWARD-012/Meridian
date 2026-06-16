from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from catalog.models import Product
from .models import Cart, CartItem


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def get_cart_with_items(user):
    cart = get_or_create_cart(user)
    return Cart.objects.prefetch_related("items__product__category").get(pk=cart.pk)


def cart_item_count(user):
    if not user.is_authenticated:
        return 0
    from django.db.models import Sum
    cart = get_or_create_cart(user)
    return cart.items.aggregate(total=Sum("quantity"))["total"] or 0


@transaction.atomic
def replace_cart_with_product(user, product_id, quantity=1):
    """Buy Now: single-product cart."""
    quantity = int(quantity)
    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")

    product = get_object_or_404(Product.objects.select_for_update(), pk=product_id, is_active=True)
    if product.stock_quantity < quantity:
        raise ValueError(f"Only {product.stock_quantity} units available.")

    cart = Cart.objects.select_for_update().get_or_create(user=user)[0]
    CartItem.objects.filter(cart=cart).delete()
    CartItem.objects.create(cart=cart, product=product, quantity=quantity)
    return get_cart_with_items(user)


@transaction.atomic
def add_to_cart(user, product_id, quantity=1):
    quantity = int(quantity)
    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")

    product = get_object_or_404(Product.objects.select_for_update(), pk=product_id, is_active=True)
    if product.stock_quantity < quantity:
        raise ValueError(f"Only {product.stock_quantity} units available.")

    cart = get_or_create_cart(user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"quantity": quantity}
    )
    if not created:
        new_qty = item.quantity + quantity
        if new_qty > product.stock_quantity:
            raise ValueError(f"Cannot add more than {product.stock_quantity} units.")
        item.quantity = new_qty
        item.save(update_fields=["quantity"])

    return get_cart_with_items(user)


@transaction.atomic
def update_cart_item(user, item_id, quantity):
    quantity = int(quantity)
    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")

    cart = get_or_create_cart(user)
    item = get_object_or_404(
        CartItem.objects.select_related("product").select_for_update(),
        pk=item_id,
        cart=cart,
    )
    product = Product.objects.select_for_update().get(pk=item.product_id)
    if quantity > product.stock_quantity:
        raise ValueError(f"Only {product.stock_quantity} units available.")

    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return get_cart_with_items(user)


@transaction.atomic
def remove_from_cart(user, item_id):
    cart = get_or_create_cart(user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    return get_cart_with_items(user)


def cart_subtotal(cart):
    total = Decimal("0.00")
    for item in cart.items.select_related("product"):
        total += item.line_total
    return total


@transaction.atomic
def clamp_cart_to_stock(user):
    """Lower cart quantities when DB stock dropped below cart qty."""
    cart = Cart.objects.select_for_update().filter(user=user).first()
    if not cart:
        return
    for item in CartItem.objects.select_for_update().filter(cart=cart).select_related("product"):
        stock = item.product.stock_quantity
        if stock < 1:
            item.delete()
        elif item.quantity > stock:
            item.quantity = stock
            item.save(update_fields=["quantity"])
