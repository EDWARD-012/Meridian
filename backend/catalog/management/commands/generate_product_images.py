from pathlib import Path

from django.core.management.base import BaseCommand

from catalog.models import Product
from catalog.product_svg import write_product_images


class Command(BaseCommand):
    help = "Generate unique SVG images for every product (main + 4 gallery views)"

    def handle(self, *args, **options):
        base = Path(__file__).resolve().parents[3] / "static" / "products"
        count = 0
        products = Product.objects.select_related("category").order_by("id")
        if not products.exists():
            self.stdout.write(self.style.WARNING("No products in DB — run seed_data first."))
            return

        for product in products:
            cat_slug = product.category.slug if product.category_id else "home"
            count += write_product_images(base, product.slug, product.name, cat_slug)

        self.stdout.write(self.style.SUCCESS(f"Generated {count} images for {products.count()} products"))
