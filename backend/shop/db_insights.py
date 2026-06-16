"""Collect schema, live data, and SQL view results for the DB Insights page."""

from decimal import Decimal

from django.apps import apps
from django.db import connection
from django.db.models import Count, Sum, Max, F, Q

from catalog.models import Category, Product, Seller, Review, ProductImage
from cart.models import Cart, CartItem
from orders.models import Address, Order, OrderItem, Payment, OrderTracking
from accounts.models import UserProfile

BUSINESS_APPS = ("catalog", "cart", "orders", "accounts")

SQL_VIEWS = {
    "v_category_sales": {
        "title": "Sales by Category",
        "description": "Revenue and order count grouped by product category (excludes cancelled orders).",
        "columns": ["Category", "Orders", "Revenue (₹)"],
        "sql": """SELECT c.name AS category_name,
       COUNT(DISTINCT oi.order_id) AS total_orders,
       SUM(oi.subtotal) AS total_revenue
FROM catalog_category c
JOIN catalog_product p ON p.category_id = c.id
JOIN orders_orderitem oi ON oi.product_id = p.id
JOIN orders_order o ON o.id = oi.order_id AND o.status != 'cancelled'
GROUP BY c.id, c.name;""",
    },
    "v_cart_summary": {
        "title": "Active Cart Summary",
        "description": "Line items, units, and cart value per logged-in user.",
        "columns": ["User", "Line items", "Units", "Cart value (₹)"],
        "sql": """SELECT u.username,
       COUNT(ci.id) AS line_items,
       SUM(ci.quantity) AS total_units,
       SUM(ci.quantity * p.price) AS cart_value
FROM auth_user u
JOIN cart_cart cart ON cart.user_id = u.id
JOIN cart_cartitem ci ON ci.cart_id = cart.id
JOIN catalog_product p ON p.id = ci.product_id
GROUP BY u.id, u.username;""",
    },
    "v_order_tracking": {
        "title": "Order Tracking Overview",
        "description": "Current order status, payment state, and tracking event count.",
        "columns": ["Order", "User", "Status", "Payment", "Amount (₹)", "Events", "Last update"],
        "sql": """SELECT o.id AS order_id, u.username, o.status,
       p.status AS payment_status, o.total_amount,
       COUNT(t.id) AS tracking_events, MAX(t.recorded_at) AS last_update
FROM orders_order o
JOIN auth_user u ON u.id = o.user_id
LEFT JOIN orders_payment p ON p.order_id = o.id
LEFT JOIN orders_ordertracking t ON t.order_id = o.id
GROUP BY o.id;""",
    },
}

TRIGGERS = [
    {
        "name": "trg_orderitem_reduce_stock",
        "table": "orders_orderitem",
        "event": "AFTER INSERT",
        "description": "Viva example only — NOT deployed in production (Django ORM decrements stock in place_order).",
    },
    {
        "name": "trg_order_status_track",
        "table": "orders_order",
        "event": "AFTER UPDATE",
        "description": "Viva example only — NOT deployed (Django creates OrderTracking rows in application code).",
    },
]


def _field_type(field):
    internal = field.get_internal_type()
    if internal in ("AutoField", "BigAutoField"):
        return "BIGINT PK"
    if internal == "CharField":
        return f"VARCHAR({getattr(field, 'max_length', '')})"
    if internal == "SlugField":
        return f"VARCHAR({getattr(field, 'max_length', '')})"
    if internal == "TextField":
        return "TEXT"
    if internal == "URLField":
        return f"VARCHAR({getattr(field, 'max_length', '')})"
    if internal == "DecimalField":
        return f"DECIMAL({field.max_digits},{field.decimal_places})"
    if internal == "PositiveIntegerField":
        return "INT UNSIGNED"
    if internal == "PositiveSmallIntegerField":
        return "SMALLINT"
    if internal == "BooleanField":
        return "BOOLEAN"
    if internal == "DateField":
        return "DATE"
    if internal == "DateTimeField":
        return "DATETIME"
    if internal == "ForeignKey":
        return "FK"
    if internal == "OneToOneField":
        return "FK (1:1)"
    return internal


def _format_cell(value):
    if value is None:
        return "—"
    if isinstance(value, Decimal):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    text = str(value)
    return text if len(text) <= 72 else text[:69] + "…"


def get_db_meta():
    vendor = connection.vendor
    engine = "SQLite" if vendor == "sqlite" else "MySQL" if vendor == "mysql" else vendor.upper()
    return {
        "engine": engine,
        "vendor": vendor,
        "name": connection.settings_dict.get("NAME", ""),
        "views_from_sql": vendor == "mysql",
    }


def get_table_schemas():
    schemas = []
    for app_label in BUSINESS_APPS:
        for model in apps.get_app_config(app_label).get_models():
            fields = []
            for field in model._meta.fields:
                info = {
                    "name": field.column,
                    "type": _field_type(field),
                    "nullable": field.null,
                    "unique": field.unique,
                }
                if field.is_relation and field.related_model:
                    info["fk"] = field.related_model._meta.db_table
                fields.append(info)
            schemas.append({
                "table": model._meta.db_table,
                "label": model._meta.verbose_name.title(),
                "model": model.__name__,
                "app": app_label,
                "fields": fields,
                "row_count": model.objects.count(),
                "sample": get_sample_rows(model),
            })
    return schemas


def get_sample_rows(model, limit=4):
    rows = []
    for obj in model.objects.all()[:limit]:
        row = {}
        for field in model._meta.fields:
            val = getattr(obj, field.name)
            if field.is_relation and val is not None:
                val = f"{val} (#{val.pk})"
            row[field.column] = _format_cell(val)
        rows.append(row)
    return rows


def _run_sql_view(name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {name} LIMIT 12")
        cols = [col[0] for col in cursor.description]
        return cols, [list(row) for row in cursor.fetchall()]


def _category_sales_orm():
    rows = []
    for cat in Category.objects.annotate(
        total_orders=Count("products__order_items__order", distinct=True, filter=~Q(products__order_items__order__status=Order.Status.CANCELLED)),
        total_revenue=Sum("products__order_items__subtotal", filter=~Q(products__order_items__order__status=Order.Status.CANCELLED)),
    ).order_by("-total_revenue"):
        if cat.total_orders:
            rows.append([cat.name, cat.total_orders, cat.total_revenue or 0])
    return rows


def _cart_summary_orm():
    rows = []
    for cart in Cart.objects.select_related("user").annotate(
        line_items=Count("items"),
        total_units=Sum("items__quantity"),
        cart_value=Sum(F("items__quantity") * F("items__product__price")),
    ).filter(line_items__gt=0):
        rows.append([cart.user.username, cart.line_items, cart.total_units or 0, cart.cart_value or 0])
    return rows


def _order_tracking_orm():
    rows = []
    for order in Order.objects.select_related("user", "payment").annotate(
        track_count=Count("tracking_events"),
        last_update=Max("tracking_events__recorded_at"),
    ).order_by("-order_date")[:12]:
        payment_status = order.payment.status if hasattr(order, "payment") else "—"
        rows.append([
            f"#{order.pk}",
            order.user.username,
            order.status,
            payment_status,
            order.total_amount,
            order.track_count,
            order.last_update.strftime("%d %b %Y %H:%M") if order.last_update else "—",
        ])
    return rows


def _format_view_row(key, row):
    if key == "v_category_sales" and len(row) >= 3:
        return [row[0], row[1], f"₹{row[2]:,.0f}"]
    if key == "v_cart_summary" and len(row) >= 4:
        return [row[0], row[1], row[2], f"₹{row[3]:,.0f}"]
    if key == "v_order_tracking" and len(row) >= 5:
        amount = row[4]
        if isinstance(amount, Decimal):
            amount = f"₹{amount:,.0f}"
        return [row[0], row[1], row[2], row[3], amount, row[5], row[6]]
    return row


def get_sql_view_results():
    results = []
    orm_fallbacks = {
        "v_category_sales": _category_sales_orm,
        "v_cart_summary": _cart_summary_orm,
        "v_order_tracking": _order_tracking_orm,
    }
    for key, meta in SQL_VIEWS.items():
        entry = {**meta, "key": key, "rows": [], "source": "orm"}
        if connection.vendor == "mysql":
            try:
                cols, rows = _run_sql_view(key)
                entry["rows"] = [_format_view_row(key, row) for row in rows]
                entry["columns"] = [c.replace("_", " ").title() for c in cols]
                entry["source"] = "sql"
            except Exception:
                entry["rows"] = [_format_view_row(key, row) for row in orm_fallbacks[key]()]
        else:
            entry["rows"] = [_format_view_row(key, row) for row in orm_fallbacks[key]()]
        results.append(entry)
    return results


def get_summary_stats():
    raw = {
        "categories": Category.objects.count(),
        "sellers": Seller.objects.count(),
        "products": Product.objects.count(),
        "reviews": Review.objects.count(),
        "product_images": ProductImage.objects.count(),
        "carts": Cart.objects.count(),
        "cart_items": CartItem.objects.count(),
        "addresses": Address.objects.count(),
        "orders": Order.objects.count(),
        "order_items": OrderItem.objects.count(),
        "payments": Payment.objects.count(),
        "tracking_events": OrderTracking.objects.count(),
        "profiles": UserProfile.objects.count(),
    }
    labels = {
        "categories": "Categories",
        "sellers": "Sellers",
        "products": "Products",
        "reviews": "Reviews",
        "product_images": "Gallery images",
        "carts": "Carts",
        "cart_items": "Cart items",
        "addresses": "Addresses",
        "orders": "Orders",
        "order_items": "Order items",
        "payments": "Payments",
        "tracking_events": "Tracking events",
        "profiles": "User profiles",
    }
    return [{"key": k, "label": labels[k], "count": v} for k, v in raw.items()]


def get_order_flow_stats():
    status_counts = dict(
        Order.objects.values_list("status").annotate(c=Count("id")).values_list("status", "c")
    )
    payment_counts = dict(
        Payment.objects.values_list("status").annotate(c=Count("id")).values_list("status", "c")
    )
    return {"order_status": status_counts, "payment_status": payment_counts}


def build_insights_context():
    stats = get_summary_stats()
    return {
        "meta": get_db_meta(),
        "stats": stats,
        "total_rows": sum(s["count"] for s in stats),
        "schemas": get_table_schemas(),
        "views": get_sql_view_results(),
        "triggers": TRIGGERS,
        "flow": get_order_flow_stats(),
    }
