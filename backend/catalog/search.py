"""Database-backed product search with relevance ranking."""

from django.db.models import Q, Count, Case, When, Value, IntegerField
from catalog.models import Category, Product
from catalog.images import product_image_url


def _tokens(query: str) -> list[str]:
    return [t.strip() for t in query.split() if t.strip()]


def product_search_filter(query: str) -> Q:
    """
    Match products where EVERY token appears in at least one of:
    name, description, category name, category slug.
    Example: "books" matches all products in Books category.
    """
    tokens = _tokens(query)
    if not tokens:
        return Q()

    combined = Q()
    for token in tokens:
        token_q = (
            Q(name__icontains=token)
            | Q(description__icontains=token)
            | Q(category__name__icontains=token)
            | Q(category__slug__icontains=token)
        )
        combined &= token_q
    return combined


def search_products(queryset, query: str):
    """Filter and rank products by relevance (all from DB)."""
    query = query.strip()
    if not query:
        return queryset.order_by("name")

    filtered = queryset.filter(product_search_filter(query)).distinct()
    tokens = _tokens(query)
    first = tokens[0] if tokens else query

    return filtered.annotate(
        relevance=Case(
            When(name__iexact=query, then=Value(0)),
            When(name__istartswith=query, then=Value(1)),
            When(name__icontains=query, then=Value(2)),
            When(category__name__iexact=first, then=Value(3)),
            When(category__name__icontains=first, then=Value(4)),
            When(description__icontains=query, then=Value(5)),
            default=Value(6),
            output_field=IntegerField(),
        )
    ).order_by("relevance", "name")


def search_categories(query: str, limit: int = 4):
    """Categories matching query from DB."""
    query = query.strip()
    if len(query) < 1:
        return Category.objects.none()

    return (
        Category.objects.filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        )
        .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
        .order_by("name")[:limit]
    )


def search_suggestions(query: str, product_limit: int = 8, category_limit: int = 4) -> dict:
    """Build suggestion payload for live search dropdown."""
    query = query.strip()
    if len(query) < 2:
        return {"query": query, "products": [], "categories": []}

    base_qs = Product.objects.filter(is_active=True).select_related("category")
    products = search_products(base_qs, query)[:product_limit]
    categories = search_categories(query, category_limit)

    return {
        "query": query,
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "price": float(p.price),
                "image_url": p.image_url or product_image_url(p.slug, p.category.slug),
                "category": p.category.name,
                "url": f"/product/{p.slug}/",
            }
            for p in products
        ],
        "categories": [
            {
                "name": c.name,
                "slug": c.slug,
                "product_count": c.product_count,
                "url": f"/?category={c.slug}",
            }
            for c in categories
        ],
    }
