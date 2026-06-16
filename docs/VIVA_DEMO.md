# Viva Demo Script

5–10 minute demonstration flow for DBMS viva.

---

## Before viva — prepare

```powershell
cd backend
# MySQL mode recommended
python manage.py migrate
python manage.py seed_data
mysql -u USER -p ecommerce_db < sql_scripts/views.sql
python manage.py runserver
```

Login: **demo / demo1234**

---

## Part 1 — Application (2 min)

1. **Homepage** — categories, product cards, search
2. **Product detail** — Add to cart (AJAX, no page reload)
3. **Cart** → **Checkout** → Razorpay demo payment
4. **Orders** → **Track order** — status timeline

---

## Part 2 — Database (3 min)

### A. DB Insights page

Open: `http://127.0.0.1:8000/db-insights/`

Show:
- ER diagram (Mermaid)
- Real table schemas
- Sample rows from DB
- SQL views section

### B. MySQL Workbench (if local MySQL)

Connect with username/password → show tables:

```
catalog_product
orders_order
cart_cartitem
orders_payment
```

Run:
```sql
SELECT * FROM v_category_sales;
SELECT * FROM v_order_tracking;
```

### C. Explain connection

> “Django ORM se connect hai — `settings.py` mein `DATABASES` config.  
> Username/password `.env` se aate hain.  
> Tables `migrate` se banti hain, data `seed_data` se.”

---

## Part 3 — SQL scripts (2 min)

| File | Explain |
|------|---------|
| `sql_scripts/schema.sql` | Reference DDL, foreign keys |
| `sql_scripts/views.sql` | 3 views for reports |
| `sql_scripts/triggers.sql` | Documented but disabled — Django handles stock |

Point to `orders/services.py` → `place_order()` for stock decrement.

---

## Part 4 — Live commands (1 min)

```powershell
# Advance order status
python manage.py advance_order 6

# Django shell
python manage.py shell
>>> from catalog.models import Product
>>> Product.objects.count()
```

---

## Common viva questions & answers

**Q: Kaun sa database use kar rahe ho?**  
A: Local test SQLite; production/viva MySQL with username/password via `mysqlclient`.

**Q: Tables kaise bani?**  
A: Django migrations (`python manage.py migrate`) — models.py se auto-generate.

**Q: Normalization?**  
A: 3NF — separate tables for category, product, order, order_item, payment; no repeating groups.

**Q: Primary / Foreign keys?**  
A: `id` PK on each table; FK e.g. `orders_orderitem.order_id` → `orders_order.id`.

**Q: Triggers kahan hain?**  
A: `triggers.sql` mein documented; production mein Django transactions use karte hain double-stock bug avoid karne ke liye.

**Q: Views?**  
A: `v_category_sales`, `v_cart_summary`, `v_order_tracking` in `views.sql`.

**Q: Cart kaise store hota hai?**  
A: `cart_cart` (1 per user) + `cart_cartitem` (product + quantity).

**Q: Payment flow?**  
A: `place_order` → `orders_payment` pending → Razorpay confirm → status success → order confirmed.

---

## See also

- [DB_SCHEMA.md](DB_SCHEMA.md)
- [SQL_SCRIPTS.md](SQL_SCRIPTS.md)
- [MYSQL_SETUP.md](MYSQL_SETUP.md)
