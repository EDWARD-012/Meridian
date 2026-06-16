from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import Category, Product, Seller, Review, ProductImage
from catalog.images import product_image_url, gallery_image_urls
from catalog.product_svg import write_product_images
from catalog.descriptions import product_description, product_highlights
from accounts.models import UserProfile
from orders.models import Address


CATEGORIES = [
    ("electronics", "Electronics", "Phones, audio, and computer accessories"),
    ("clothing", "Clothing", "Apparel, footwear, and fashion"),
    ("home", "Home & Living", "Kitchen, decor, and furniture"),
    ("books", "Books", "Technical and academic books"),
    ("sports", "Sports & Fitness", "Equipment and activewear"),
    ("beauty", "Beauty & Care", "Skincare and grooming"),
]

SELLERS = [
    ("techhub-india", "TechHub India", "electronics", "4.6", 1250, 8500, "Authorized electronics seller with genuine products."),
    ("fashionlane", "FashionLane Official", "clothing", "4.4", 890, 12000, "Trendy apparel and footwear with easy returns."),
    ("homecomfort", "HomeComfort Store", "home", "4.5", 620, 5400, "Quality home and kitchen essentials."),
    ("bookworm-official", "BookWorm Official", "books", "4.7", 2100, 22000, "Academic and tech books from trusted publishers."),
    ("fitlife-sports", "FitLife Sports", "sports", "4.3", 540, 6800, "Sports gear for fitness enthusiasts and athletes."),
    ("glowcare-beauty", "GlowCare Beauty", "beauty", "4.5", 780, 9100, "Skincare and grooming products — dermatologist approved."),
]

PRODUCTS = [
    ("electronics", "Wireless Earbuds Pro", 2499, 50),
    ("electronics", "Mechanical Keyboard RGB", 4599, 30),
    ("electronics", "USB-C Hub 7-in-1", 1899, 45),
    ("electronics", "Bluetooth Speaker Mini", 1999, 40),
    ("electronics", "Smart Watch Series X", 8999, 15),
    ("electronics", "Laptop Stand Aluminum", 1499, 60),
    ("electronics", "Webcam HD 1080p", 3299, 25),
    ("electronics", "Power Bank 20000mAh", 1799, 55),
    ("clothing", "Classic Denim Jacket", 3299, 25),
    ("clothing", "Cotton Crew Tee White", 799, 100),
    ("clothing", "Running Sneakers Pro", 5499, 20),
    ("clothing", "Formal Shirt Slim Fit", 1899, 35),
    ("clothing", "Winter Hoodie Grey", 2499, 40),
    ("clothing", "Leather Belt Brown", 999, 50),
    ("clothing", "Sports Shorts Black", 899, 45),
    ("clothing", "Canvas Sneakers Casual", 2199, 30),
    ("home", "Ceramic Coffee Mug Set", 1299, 60),
    ("home", "Desk Lamp Minimal LED", 2199, 35),
    ("home", "Non-stick Pan 28cm", 1599, 40),
    ("home", "Bed Sheet Set Queen", 2799, 22),
    ("home", "Storage Baskets Set of 3", 999, 48),
    ("home", "Wall Clock Modern", 1299, 33),
    ("home", "Throw Pillow Covers 2pc", 799, 70),
    ("books", "Clean Code Handbook", 899, 80),
    ("books", "System Design Interview", 1199, 55),
    ("books", "Python Crash Course", 749, 90),
    ("books", "Database Internals", 1499, 40),
    ("books", "Operating Systems Concepts", 1299, 35),
    ("books", "Machine Learning Basics", 1699, 28),
    ("sports", "Yoga Mat Premium 6mm", 1299, 50),
    ("sports", "Dumbbells Pair 5kg", 2499, 20),
    ("sports", "Cricket Bat Kashmir Willow", 3499, 15),
    ("sports", "Football Size 5", 999, 45),
    ("sports", "Resistance Bands Set", 799, 60),
    ("sports", "Gym Gloves Pair", 599, 55),
    ("sports", "Skipping Rope Speed", 399, 80),
    ("beauty", "Face Wash Neem 150ml", 349, 100),
    ("beauty", "Moisturizer SPF 30", 599, 75),
    ("beauty", "Beard Oil Natural", 449, 65),
    ("beauty", "Hair Serum Anti-frizz", 699, 50),
    ("beauty", "Sunscreen Gel 50 SPF", 499, 85),
    ("beauty", "Lip Balm Pack of 3", 299, 120),
    ("beauty", "Body Lotion Cocoa 400ml", 399, 90),
]

REVIEW_TEMPLATES = [
    (5, "Excellent product!", "Exactly as described. Quality is top notch. Would buy again."),
    (5, "Perfect for daily use", "Been using for a month now. No complaints at all."),
    (4, "Good value for money", "Solid product at this price point. Delivery was fast."),
    (4, "Pretty good", "Minor packaging issue but product itself is great."),
    (3, "Decent", "Works fine but expected slightly better quality."),
    (5, "Highly recommended", "Best purchase this month. Seller was very responsive."),
]

DEMO_ADDRESSES = [
    ("Ravi Kumar", "42 MG Road, Sector 14", "Gurgaon", "Haryana", "122001", True),
    ("Ravi Kumar", "Flat 301, Lake View Apartments", "Bangalore", "Karnataka", "560001", False),
]


def make_slug(name: str) -> str:
    return name.lower().replace(" ", "-").replace("&", "and").replace(",", "")


class Command(BaseCommand):
    help = "Seed categories, sellers, products with matched images, reviews"

    def handle(self, *args, **options):
        cat_map = {}
        for slug, name, desc in CATEGORIES:
            cat, _ = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "description": desc}
            )
            cat_map[slug] = cat

        seller_map = {}
        for slug, name, cat_slug, rating, total_ratings, total_sales, desc in SELLERS:
            seller, _ = Seller.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "rating": rating,
                    "total_ratings": total_ratings,
                    "total_sales": total_sales,
                    "description": desc,
                    "verified": True,
                    "member_since": date(2019, 3, 15),
                    "fulfillment": "Meridian Fulfilled",
                    "city": "Mumbai",
                },
            )
            seller_map[cat_slug] = seller

        reviewer_names = ["reviewer_amit", "reviewer_priya", "reviewer_rahul"]
        reviewers = []
        for uname in reviewer_names:
            u, created = User.objects.get_or_create(username=uname, defaults={"email": f"{uname}@shop.local"})
            if created:
                u.set_password("demo1234")
                u.save()
            reviewers.append(u)

        for cat_slug, name, price, stock in PRODUCTS:
            slug = make_slug(name)
            product, _ = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "category": cat_map[cat_slug],
                    "seller": seller_map.get(cat_slug),
                    "name": name,
                    "description": product_description(name, cat_map[cat_slug].name, price),
                    "highlights": product_highlights(name, cat_map[cat_slug].name),
                    "price": price,
                    "stock_quantity": stock,
                    "image_url": product_image_url(slug, cat_slug),
                    "is_active": True,
                },
            )
            ProductImage.objects.filter(product=product).delete()
            for i, url in enumerate(gallery_image_urls(slug, cat_slug)):
                ProductImage.objects.create(
                    product=product,
                    image_url=url,
                    alt_text=f"{name} — view {i + 1}",
                    sort_order=i,
                    is_primary=(i == 0),
                )
            for i, (rating, title, comment) in enumerate(REVIEW_TEMPLATES[:3]):
                reviewer = reviewers[i % len(reviewers)]
                Review.objects.update_or_create(
                    product=product,
                    user=reviewer,
                    defaults={
                        "rating": rating,
                        "title": title,
                        "comment": comment,
                        "verified_purchase": True,
                        "helpful_count": (rating * 3 + i),
                    },
                )

        user, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@shop.local", "first_name": "Demo", "is_staff": True},
        )
        if created:
            user.set_password("demo1234")
        else:
            user.set_password("demo1234")
        if not user.is_staff:
            user.is_staff = True
        user.save()
        UserProfile.objects.get_or_create(user=user, defaults={"phone": "9876543210"})

        for full_name, line1, city, state, pincode, is_default in DEMO_ADDRESSES:
            Address.objects.update_or_create(
                user=user,
                line1=line1,
                defaults={
                    "full_name": full_name,
                    "city": city,
                    "state": state,
                    "pincode": pincode,
                    "is_default": is_default,
                },
            )

        img_base = Path(__file__).resolve().parents[3] / "static" / "products"
        img_count = 0
        for product in Product.objects.select_related("category"):
            cat_slug = product.category.slug if product.category_id else "home"
            img_count += write_product_images(img_base, product.slug, product.name, cat_slug)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete — Sellers: {Seller.objects.count()}, "
            f"Products: {Product.objects.filter(is_active=True).count()}, "
            f"Reviews: {Review.objects.count()}, Images: {img_count}"
        ))
        self.stdout.write("Login: demo / demo1234")
