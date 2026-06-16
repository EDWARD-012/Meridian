# Local Development

---

## Requirements

- Python 3.11+
- pip
- (Optional) MySQL / XAMPP for real DB viva setup

---

## Setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

---

## Mode A — SQLite (fastest)

`.env`:
```env
USE_SQLITE=True
DEBUG=True
```

```powershell
$env:USE_SQLITE="True"
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Database file: `backend/db.sqlite3`

---

## Mode B — MySQL (viva / real SQL)

See [MYSQL_SETUP.md](MYSQL_SETUP.md)

```env
USE_SQLITE=False
DB_NAME=ecommerce_db
DB_USER=meridian_user
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_PORT=3306
```

```powershell
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

---

## Useful commands

| Command | Description |
|---------|-------------|
| `python manage.py runserver` | Start dev server :8000 |
| `python manage.py shell` | Django ORM shell |
| `python manage.py createsuperuser` | Admin user |
| `python manage.py advance_order 1` | Demo: next order status |
| `python manage.py check` | Validate project |

---

## URLs (local)

| URL | Page |
|-----|------|
| `/` | Home — product grid |
| `/product/<slug>/` | Product detail |
| `/cart/` | Shopping cart |
| `/checkout/` | Checkout |
| `/profile/` | User profile |
| `/orders/` | Order history |
| `/db-insights/` | DB schema & SQL (staff) |
| `/health/` | Health check JSON |
| `/admin/` | Django admin |

---

## Demo login

| User | Password | Role |
|------|----------|------|
| demo | demo1234 | Staff (DB Insights access) |

---

## Environment variables reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | dev fallback | Session/crypto key |
| `DEBUG` | `True` | Never `True` in production |
| `USE_SQLITE` | `False` | `True` = SQLite file |
| `DATABASE_URL` | — | Full DB URL (overrides DB_*) |
| `DB_NAME` | ecommerce_db | MySQL database name |
| `DB_USER` | root | MySQL username |
| `DB_PASSWORD` | — | MySQL password |
| `DB_HOST` | 127.0.0.1 | MySQL host |
| `DB_PORT` | 3306 | MySQL port |
| `ALLOWED_HOSTS` | localhost | Comma-separated |
| `CSRF_TRUSTED_ORIGINS` | — | Required when DEBUG=False |

---

## Static / media

- CSS/JS: `backend/static/`
- Product images: `backend/static/products/items/*.svg`
- Collected for production: `python manage.py collectstatic` → `staticfiles/`

---

## See also

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
