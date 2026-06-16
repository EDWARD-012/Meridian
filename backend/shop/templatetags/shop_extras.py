from django import template

register = template.Library()


@register.filter
def in_cart(cart_items, product_id):
    if not cart_items:
        return False
    return int(product_id) in cart_items


@register.filter
def cart_qty(cart_items, product_id):
    if not cart_items:
        return 0
    item = cart_items.get(int(product_id))
    return item["quantity"] if item else 0


@register.filter
def cart_item_id(cart_items, product_id):
    if not cart_items:
        return None
    item = cart_items.get(int(product_id))
    return item["item_id"] if item else None


@register.filter
def available_stock(product, cart_items):
    """DB stock minus quantity already in this user's cart."""
    in_cart = 0
    if cart_items:
        item = cart_items.get(int(product.id))
        if item:
            in_cart = item["quantity"]
    return max(0, product.stock_quantity - in_cart)


@register.filter
def product_img(product):
    if product.image_url:
        return product.image_url
    from catalog.images import product_image_url
    cat_slug = product.category.slug if product.category_id else ""
    return product_image_url(product.slug, cat_slug)


@register.filter
def list_price(price):
    """Strikethrough MRP (~22% markup) for display."""
    try:
        from decimal import Decimal
        return int(Decimal(str(price)) * Decimal("1.22"))
    except (TypeError, ValueError):
        return price


@register.filter
def stars(rating):
    """Render star string for rating 0-5."""
    try:
        r = float(rating)
    except (TypeError, ValueError):
        r = 0
    full = int(r)
    half = 1 if r - full >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty


@register.simple_tag
def cart_qty_range(item):
    """Qty dropdown options capped at available stock."""
    stock = max(0, int(item.product.stock_quantity))
    cap = min(stock, 99) if stock else 1
    return range(1, cap + 1)


@register.filter
def star_percent(reviews, star_num):
    """Percentage of reviews with given star rating."""
    total = reviews.count()
    if not total:
        return 0
    count = reviews.filter(rating=star_num).count()
    return int(count * 100 / total)
