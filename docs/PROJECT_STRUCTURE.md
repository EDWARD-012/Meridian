# Project Structure

```
DBMS/
├── README.md                 # Main entry — start here
├── render.yaml               # Render deploy config (web + cron)
├── docs/                     # All documentation
│   ├── PROJECT_STRUCTURE.md  # This file
│   ├── DB_SCHEMA.md
│   ├── MYSQL_SETUP.md
│   ├── SQL_SCRIPTS.md
│   ├── DEPLOYMENT.md
│   ├── LOCAL_DEVELOPMENT.md
│   └── VIVA_DEMO.md
│
└── backend/                  # ★ Django application (everything runs here)
    ├── manage.py
    ├── requirements.txt
    ├── build.sh              # Post-deploy helper (migrate; seed optional)
    ├── .env.example          # Environment template
    ├── config/               # Django project settings
    │   ├── settings.py       # DB connection, security, static
    │   ├── urls.py           # Root URLs + /health/
    │   └── wsgi.py           # Production entry (gunicorn)
    │
    ├── accounts/             # User profile extension
    ├── catalog/              # Products, categories, sellers, reviews
    ├── cart/                 # Shopping cart models + services
    ├── orders/               # Orders, payments, addresses, tracking
    ├── shop/                 # All page views, forms, DB Insights
    │
    ├── sql_scripts/          # Raw SQL for viva / MySQL Workbench
    │   ├── schema.sql
    │   ├── views.sql
    │   └── triggers.sql
    │
    ├── templates/            # HTML pages
    │   ├── base.html
    │   ├── shop/             # home, cart, checkout, profile, orders…
    │   ├── accounts/         # login, register
    │   └── partials/         # product_card, product_image
    │
    └── static/               # CSS, JS, product SVG images
        ├── css/
        ├── js/
        └── products/items/   # Generated product images (*.svg)
```

---

## Django apps — responsibility

| App | Models | Purpose |
|-----|--------|---------|
| **accounts** | `UserProfile` | Phone number, profile metadata |
| **catalog** | `Category`, `Product`, `Seller`, `Review`, `ProductImage` | Product catalog |
| **cart** | `Cart`, `CartItem` | Per-user shopping cart |
| **orders** | `Address`, `Order`, `OrderItem`, `Payment`, `OrderTracking` | Checkout & fulfillment |
| **shop** | (no models) | Views, URLs, forms, DB Insights page |

---

## Request flow

```
Browser
  → config/urls.py
  → shop/urls.py (home, cart, checkout, profile, razorpay…)
  → shop/views.py
  → cart/services.py or orders/services.py (business logic)
  → Django ORM → MySQL / SQLite
  → templates/*.html + static/
```

---

## Important files

| File | Role |
|------|------|
| `config/settings.py` | `DATABASES`, `SECRET_KEY`, production security |
| `shop/views.py` | All main page logic |
| `orders/services.py` | `place_order`, payment confirm/fail, stock |
| `cart/services.py` | Add/update cart, buy-now |
| `catalog/management/commands/seed_data.py` | Demo data loader |
| `shop/db_insights.py` | DB Insights page data (tables, ER, SQL) |
| `catalog/product_svg.py` | Generates product SVG images |

---

## Management commands

| Command | Purpose |
|---------|---------|
| `python manage.py migrate` | Create/update DB tables |
| `python manage.py seed_data` | Load demo products, users, reviews |
| `python manage.py advance_order <id>` | Move order to next status (viva) |
| `python manage.py cancel_stale_orders` | Cancel unpaid Razorpay orders (cron) |

---

## What is NOT used

- `frontend/` — old React/Three.js experiment; ignore for deploy and viva.
