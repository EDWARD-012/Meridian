from django.db.models import Sum, Count, Q
from cart.services import get_or_create_cart
from catalog.models import Category


def cart_summary(request):
    count = 0
    cart_items = {}
    subtotal = 0

    if request.user.is_authenticated:
        cart = get_or_create_cart(request.user)
        count = cart.items.aggregate(total=Sum("quantity"))["total"] or 0
        for item in cart.items.select_related("product"):
            cart_items[item.product_id] = {
                "item_id": item.id,
                "quantity": item.quantity,
                "line_total": item.line_total,
            }
            subtotal += item.line_total

    return {
        "cart_count": count,
        "cart_items": cart_items,
        "cart_subtotal": subtotal,
        "nav_categories": Category.objects.annotate(
            product_count=Count("products", filter=Q(products__is_active=True))
        ).order_by("name")[:8],
    }
