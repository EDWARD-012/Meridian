"""Local static product images — one unique SVG per product."""

STATIC_PREFIX = "/static/products/items"


def product_image_url(slug: str, category_slug: str = "") -> str:
    return f"{STATIC_PREFIX}/{slug}.svg"


def gallery_image_urls(slug: str, category_slug: str = "") -> list[str]:
    return [f"{STATIC_PREFIX}/{slug}-v{i}.svg" for i in range(1, 5)]
