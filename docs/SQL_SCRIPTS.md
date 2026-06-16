# SQL Scripts Guide

All raw SQL files live in:

```
backend/sql_scripts/
├── schema.sql     # Table definitions (reference)
├── views.sql      # MySQL views (run on cloud/local MySQL)
└── triggers.sql   # Viva documentation — stock triggers DISABLED
```

---

## Overview

| Script | Run on fresh Django project? | Purpose |
|--------|------------------------------|---------|
| `schema.sql` | **No** (use `migrate` instead) | Viva reference DDL |
| `views.sql` | **Yes** (after migrate + seed) | Analytics views |
| `triggers.sql` | **DROP only** in production | Remove old triggers if any |

Django **`python manage.py migrate`** creates all tables including `auth_user`, `django_migrations`, etc.  
`schema.sql` only documents **business tables** — not a replacement for migrate.

---

## 1. `schema.sql`

**Path:** `backend/sql_scripts/schema.sql`

**What it does:**
- Creates database `ecommerce_db` (if not exists)
- Documents CREATE TABLE for:
  - `catalog_category`, `catalog_product`
  - `cart_cart`, `cart_cartitem`
  - `orders_address`, `orders_order`, `orders_orderitem`
  - `orders_payment`, `orders_ordertracking`
- Defines FOREIGN KEYs and INDEXes

**When to use:**
- Viva presentation — “yeh hamara schema hai”
- MySQL Workbench mein design dikhana
- Written exam / report attachment

**How to run (optional — only if NOT using Django migrate):**

```bash
mysql -u root -p < backend/sql_scripts/schema.sql
```

**Recommended instead:**

```powershell
cd backend
python manage.py migrate
```

---

## 2. `views.sql`

**Path:** `backend/sql_scripts/views.sql`

**What it does:** Creates 3 MySQL **views**:

### `v_category_sales`
- Revenue per category
- Joins: `catalog_category` → `catalog_product` → `orders_orderitem` → `orders_order`
- Excludes cancelled orders

```sql
SELECT * FROM v_category_sales;
```

### `v_cart_summary`
- Per-user cart: line items, total units, cart value
- Joins: `auth_user` → `cart_cart` → `cart_cartitem` → `catalog_product`

```sql
SELECT * FROM v_cart_summary;
```

### `v_order_tracking`
- Order overview: username, payment status, tracking event count, last update

```sql
SELECT * FROM v_order_tracking;
```

**When to run:** After `migrate` + `seed_data` (tables must exist with data).

**How to run:**

```powershell
cd backend
mysql -u meridian_user -p ecommerce_db < sql_scripts/views.sql
```

Or paste into MySQL Workbench → Execute.

**App integration:** `/db-insights/` page shows these views on MySQL. On SQLite, Django ORM fallback use hota hai.

---

## 3. `triggers.sql`

**Path:** `backend/sql_scripts/triggers.sql`

**What it does TODAY:**
- **DROP** old triggers `trg_orderitem_reduce_stock` and `trg_order_status_track`
- Comments explain optional audit trigger (disabled)

**Why stock trigger is disabled:**

Django already decrements stock in `orders/services.py` → `place_order()`.  
Agar MySQL trigger bhi stock ghata de, to **double decrement** ho jata hai.

**Production rule:** Stock management = **Django ORM only**.

**When to run:** Only if you previously deployed old triggers on cloud MySQL:

```powershell
mysql -u USER -p ecommerce_db < sql_scripts/triggers.sql
```

**Viva explanation:** “Triggers SQL file mein documented hain, lekin production mein Django transactions use karte hain consistency ke liye.”

---

## Script vs Django — who does what?

| Task | Handled by |
|------|------------|
| Create tables | `python manage.py migrate` |
| Insert demo data | `python manage.py seed_data` |
| Decrement stock on order | `orders/services.py` (`place_order`) |
| Restore stock on payment fail | `orders/services.py` (`fail_razorpay_payment`) |
| Category sales report | `views.sql` → `v_category_sales` |
| Cancel stale unpaid orders | `python manage.py cancel_stale_orders` (cron) |

---

## File flow diagram

```
seed_data.py          →  INSERT rows into tables
place_order()         →  INSERT order + UPDATE stock
views.sql             →  CREATE VIEW (read-only reports)
triggers.sql          →  DROP old triggers (safety)
schema.sql            →  Reference documentation only
```

---

## Viva demo queries

```sql
-- After views.sql
SELECT * FROM v_category_sales ORDER BY total_revenue DESC;

-- Raw join (without view)
SELECT p.name, oi.quantity, oi.subtotal
FROM orders_orderitem oi
JOIN catalog_product p ON p.id = oi.product_id
WHERE oi.order_id = 1;

-- Low stock alert
SELECT name, stock_quantity FROM catalog_product WHERE stock_quantity < 10;
```

---

## See also

- [DB_SCHEMA.md](DB_SCHEMA.md) — full table documentation
- [MYSQL_SETUP.md](MYSQL_SETUP.md) — connect to MySQL
- UI: `/db-insights/` — ER diagram + live data
