# MySQL Setup — Virtual / Real SQL Database

Yeh guide batati hai kaise **username + password** wale MySQL se project connect karein (viva aur production ke liye).

---

## SQLite vs MySQL — kaunsa kab?

| Mode | When | Connection |
|------|------|------------|
| **SQLite** | Quick local test | File `backend/db.sqlite3` — no login |
| **MySQL** | Viva, production, DBMS demo | Host + username + password |

Viva mein **MySQL** dikhana zyada professional hai — Workbench se tables, views, queries dikha sakte ho.

---

## Option 1 — Local MySQL (XAMPP) — recommended for viva

### Step 1: Install XAMPP

1. Download [XAMPP](https://www.apachefriends.org/) for Windows
2. Install → open **XAMPP Control Panel**
3. Start **MySQL**

MySQL runs on `127.0.0.1:3306` with default user `root` (often empty password locally).

### Step 2: Create database & user

Open **phpMyAdmin** (`http://localhost/phpmyadmin`) or MySQL shell:

```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'meridian_user'@'localhost' IDENTIFIED BY 'StrongPass123!';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'meridian_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 3: Configure Django

`backend/.env` file banao (copy from `.env.example`):

```env
SECRET_KEY=your-local-secret-key-min-50-chars
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

USE_SQLITE=False

DB_ENGINE=django.db.backends.mysql
DB_NAME=ecommerce_db
DB_USER=meridian_user
DB_PASSWORD=StrongPass123!
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Step 4: Install MySQL driver & migrate

```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Step 5: Verify in MySQL Workbench

1. Connect: Host `127.0.0.1`, User `meridian_user`, Password `StrongPass123!`
2. Database: `ecommerce_db`
3. Tables dikhengi: `catalog_product`, `orders_order`, `cart_cartitem`, etc.

---

## Option 2 — Cloud MySQL (Render / Railway / PlanetScale)

Production ya remote “virtual DB” ke liye cloud provider se MySQL URL milta hai.

### Example `.env` (Render)

```env
USE_SQLITE=False
DEBUG=False
SECRET_KEY=long-random-secret
ALLOWED_HOSTS=your-app.onrender.com,.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com

DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/ecommerce_db
```

Django `dj-database-url` se automatically parse karta hai (`config/settings.py`).

---

## Django mein connection kaise hota hai?

```
.env file
    ↓
python-decouple reads variables
    ↓
config/settings.py → DATABASES dict
    ↓
mysqlclient driver (requirements.txt)
    ↓
MySQL Server (username + password auth)
```

Code mein har jagah **Django ORM** use hota hai:

```python
Product.objects.filter(is_active=True)
Order.objects.select_related("payment")
```

Raw SQL optional hai — views/SQL scripts ke liye.

---

## Connection priority (`settings.py`)

```
1. USE_SQLITE=True     → SQLite file
2. DATABASE_URL set    → Parse URL (cloud)
3. Else                → DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
```

---

## Common errors

| Error | Fix |
|-------|-----|
| `Can't connect to MySQL server` | XAMPP MySQL start karo |
| `Access denied for user` | Username/password `.env` check karo |
| `Unknown database` | `CREATE DATABASE ecommerce_db` run karo |
| `mysqlclient` install fail (Windows) | Use pre-built wheel or install Visual C++ Build Tools |

---

## After MySQL connect — optional SQL scripts

```powershell
# MySQL CLI se views install (viva)
mysql -u meridian_user -p ecommerce_db < sql_scripts/views.sql
```

Details: [SQL_SCRIPTS.md](SQL_SCRIPTS.md)

---

## DB Insights page

Browser mein (staff user):

```
http://127.0.0.1:8000/db-insights/
```

Login: `demo / demo1234` — shows live tables, ER diagram, sample SQL.

---

## See also

- [DB_SCHEMA.md](DB_SCHEMA.md) — table list & ER
- [DEPLOYMENT.md](DEPLOYMENT.md) — Render + cloud MySQL
