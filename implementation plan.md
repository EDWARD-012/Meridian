# E-Commerce DBMS — Implementation Plan

> **Approach:** Ek step complete karo → test karo → next step. Har step ke end mein checklist tick karo.

---

## Current Problems (User Feedback)

| # | Problem | Root Cause |
|---|---------|------------|
| 1 | DB mein rows kam / gayab | `seed_data` sirf 10 products load karta hai; purana data overwrite nahi hota properly |
| 2 | Add to cart ke baad qty same card pe nahi badalti | Product card sirf "Add" button dikhata hai; cart DB se map nahi hota template mein |
| 3 | Razorpay fake demo nahi | Payment sirf COD/UPI select hai; koi Razorpay UI flow nahi |
| 4 | Items bahut kam | Seed script chhota hai |
| 5 | Saved address select ke baad bhi naya address maangta | Form UI hamesha new address fields dikhata hai; demo user ke paas saved address bhi nahi |
| 6 | UI boring / DB focus nahi | Koi live DB stats, SQL-driven insights nahi |

---

## Architecture (Final — Single Django App)

```
backend/
├── catalog/          → Product, Category (DB)
├── cart/             → Cart, CartItem + services.py
├── orders/           → Order, Payment, OrderTracking, Address
├── shop/             → Template views, forms, fake Razorpay
├── sql_scripts/      → schema.sql, views.sql, triggers.sql
├── templates/        → Plain HTML
└── static/css/       → Plain CSS (+ minimal JS where needed)
```

**Deploy:** Render — 1 service, Cloud MySQL via `DATABASE_URL`

---

## Phase 1 — Database & Seed (DB First)

### Step 1.1 — Expand seed data
**Prompt:** *"seed_data.py mein 6 categories aur 40+ products add karo. Demo user ke liye 2 saved addresses seed karo. Command output mein counts print karo."*

**Files:** `catalog/management/commands/seed_data.py`

**Acceptance:**
- [ ] 6 categories visible in DB
- [ ] 40+ products with varied price/stock
- [ ] `demo` user has 2 addresses in `orders_address`
- [ ] `python manage.py seed_data` prints row counts

### Step 1.2 — SQL views align with Django
**Prompt:** *"sql_scripts/views.sql ko verify karo aur shop home par raw SQL se category sales + cart summary stats dikhao."*

**Files:** `sql_scripts/views.sql`, `shop/views.py`, `templates/shop/home.html`

**Acceptance:**
- [ ] Home page shows live DB stats (products, categories, orders count)
- [ ] Optional: category-wise product count from DB query

---

## Phase 2 — Cart UX (DB CartItem → UI)

### Step 2.1 — Cart map in templates
**Prompt:** *"Context processor mein cart_items dict banao {product_id: {item_id, qty}}. Product card pe agar cart mein hai to +/- qty controls dikhao, warna Add to cart."*

**Files:** `shop/context_processors.py`, `partials/product_card.html`, `shop/product_detail.html`, `shop/views.py` (cart_update redirect to referer)

**Acceptance:**
- [ ] Add to cart → same card pe qty 1 dikhe (+/- buttons)
- [ ] Qty change DB `cart_cartitem` update kare
- [ ] Navbar badge bhi update ho
- [ ] Remove at qty 0 or minus button

### Step 2.2 — Cart update from home (no cart page redirect)
**Prompt:** *"cart_update aur cart_add redirect referer pe karein, messages dikhein."*

**Acceptance:**
- [ ] Home se qty change → home pe hi rehna
- [ ] Stock limit error message

---

## Phase 3 — Checkout & Address Fix

### Step 3.1 — Saved address toggle
**Prompt:** *"Checkout template: saved address select hone par new address fields hide karo (JS). Backend: use_saved=True ho to address_form validate mat karo."*

**Files:** `templates/shop/checkout.html`, `static/js/checkout.js`, `shop/views.py`

**Acceptance:**
- [ ] Checkbox ON → new address fields hidden
- [ ] Checkbox OFF → new address fields visible
- [ ] Saved address se order place ho without filling new fields

### Step 3.2 — Address cards UI
**Prompt:** *"Saved addresses ko radio card list ki tarah dikhao, default selected."*

---

## Phase 4 — Razorpay Fake Demo Payment

### Step 4.1 — Payment model update
**Prompt:** *"Payment.Method mein RAZORPAY add karo. Migration run karo."*

### Step 4.2 — Fake Razorpay checkout page
**Prompt:** *"Checkout mein Razorpay select → order create (payment pending) → redirect fake Razorpay page (Razorpay jaisa UI plain HTML/CSS). Pay button → payment success + order confirmed + fake txn id DB mein save."*

**Files:** `templates/shop/razorpay_pay.html`, `shop/views.py`, `orders/services.py`

**Acceptance:**
- [ ] Razorpay option checkout mein
- [ ] Fake payment page dikhe (logo, amount, Pay Now)
- [ ] Success → `orders_payment.status = success`, `transaction_id = pay_xxxxx`
- [ ] Order tracking event add ho

### Step 4.3 — Payment failed demo (optional)
**Prompt:** *"Fake Razorpay page par 'Simulate Fail' button → payment failed status."*

---

## Phase 5 — UI Polish (DB-Focused Theme)

### Step 5.1 — Home redesign
**Prompt:** *"Hero mein DB stats panel, category chips, product grid with stock badges. No 3D. Charcoal + copper theme."*

### Step 5.2 — DB Insights page (Viva)
**Prompt:** *"/db-insights/ page: raw SQL views results table mein — v_category_sales, v_cart_summary. Sirf staff/login required."*

**Files:** `shop/views.py`, `templates/shop/db_insights.html`

---

## Phase 6 — Production Hardening

### Step 6.1 — Bug sweep
- Transaction atomic on all cart/order ops
- select_for_update on stock
- Form CSRF on all POSTs

### Step 6.2 — Render deploy
- `render.yaml` single service
- `DATABASE_URL` for MySQL
- Google Script ping `/health/`

---

## Recursive Work Order (Priority)

```
Step 1.1  →  Step 2.1  →  Step 3.1  →  Step 4.2  →  Step 1.2  →  Step 5.1  →  Step 5.2  →  Step 6.1
```

Har step ke baad:
```powershell
cd backend
$env:USE_SQLITE="True"
python manage.py seed_data   # if step 1
python manage.py runserver
```

---

## Demo Credentials

| User | Password | Notes |
|------|----------|-------|
| demo | demo1234 | 2 saved addresses, use for checkout test |

---

## Status Tracker

| Step | Status | Done Date |
|------|--------|-----------|
| 1.1 Expand seed | ✅ Done | 48 products, 6 categories, demo addresses |
| 1.2 DB stats on home | ✅ Done | Live stats panel |
| 2.1 Inline cart qty | ✅ Done | +/- on product card |
| 2.2 Referer redirect | ✅ Done | Stays on same page |
| 3.1 Saved address fix | ✅ Done | JS hide + backend skip |
| 4.1 Razorpay method | ✅ Done | Payment.Method.RAZORPAY |
| 4.2 Fake Razorpay UI | ✅ Done | Demo pay/fail page |
| 5.1 UI polish | ✅ Done | DB panel, address cards |
| 5.2 DB insights page | ✅ Done | /db-insights/ |
| 6.1 Bug sweep | 🔄 Ongoing | Test full flow |

---

*Last updated: Steps 1.1–5.2 implemented. Next: full flow test + Render deploy.*
