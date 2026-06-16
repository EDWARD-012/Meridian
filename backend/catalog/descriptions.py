"""Rich product descriptions stored in DB — generated per product name & category."""


def product_description(name: str, category_name: str, price: int) -> str:
    return (
        f"{name} is a carefully sourced {category_name.lower()} product from our verified seller network. "
        f"Priced at ₹{price}, it offers excellent value for everyday use. "
        f"Each unit passes quality checks before listing. Suitable for personal use or gifting. "
        f"Stored and fulfilled through our warehouse with proper inventory tracking in the database."
    )


def product_highlights(name: str, category_name: str) -> str:
    common = [
        f"Genuine {category_name.lower()} product — quality assured",
        "Secure packaging with damage-free delivery",
        "Easy returns within 7 days if unsatisfied",
        "Inventory synced live from MySQL database",
    ]
    category_extra = {
        "Electronics": ["1-year manufacturer warranty", "Compatible with standard Indian power outlets"],
        "Clothing": ["Breathable fabric for all-day comfort", "Multiple size options available on request"],
        "Home & Living": ["Easy to clean and maintain", "Fits modern home décor styles"],
        "Books": ["Latest edition with clear print", "Ideal for students and professionals"],
        "Sports & Fitness": ["Durable build for regular training", "Lightweight and portable"],
        "Beauty & Care": ["Dermatologically tested formula", "Suitable for daily skincare routine"],
    }
    extras = category_extra.get(category_name, [])
    lines = common[:2] + extras + [f"Perfect choice if you need a reliable {name.lower()}"]
    return "\n".join(lines[:6])
