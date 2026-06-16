# Meridian E-Commerce DBMS

College **DBMS + E-Commerce** project — Django, MySQL/SQLite, Amazon-style UI, Razorpay demo checkout, and **DB Insights** page for viva.

> **Active app:** `backend/` only. The `frontend/` folder is unused (old React experiment).

---

## Quick start (local)

```powershell
cd backend
pip install -r requirements.txt
copy .env.example .env

$env:USE_SQLITE="True"
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open **http://127.0.0.1:8000**

| Login | Password | Notes |
|-------|----------|-------|
| `demo` | `demo1234` | Staff user — can open **DB Insights** |

---

## Documentation

| Document | What it covers |
|----------|----------------|
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Folder layout, apps, key files |
| [docs/DB_SCHEMA.md](docs/DB_SCHEMA.md) | Tables, relationships, ER diagram |
| [docs/MYSQL_SETUP.md](docs/MYSQL_SETUP.md) | Virtual/real MySQL — username, password, connect |
| [docs/SQL_SCRIPTS.md](docs/SQL_SCRIPTS.md) | Every `.sql` file — location & purpose |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Render deploy step-by-step |
| [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) | Dev workflow, commands, env vars |
| [docs/VIVA_DEMO.md](docs/VIVA_DEMO.md) | Viva demo script (orders, SQL, DB Insights) |

---

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5 |
| Frontend | Django templates + CSS + vanilla JS |
| Database (local) | SQLite (`db.sqlite3`) |
| Database (production / viva) | **MySQL 8** (username + password) |
| Static files | WhiteNoise |
| Deploy | **Render** (`render.yaml`) |

---

## Database modes

```
USE_SQLITE=True   →  SQLite file (no username/password) — quick local test
USE_SQLITE=False  →  MySQL via DATABASE_URL or DB_USER/DB_PASSWORD
```

See [docs/MYSQL_SETUP.md](docs/MYSQL_SETUP.md) for full MySQL connection guide.

---

## SQL scripts location

```
backend/sql_scripts/
├── schema.sql    # Reference DDL (tables)
├── views.sql     # MySQL views (viva)
└── triggers.sql  # Documentation only — do NOT enable stock trigger in production
```

Details: [docs/SQL_SCRIPTS.md](docs/SQL_SCRIPTS.md)

---

## Deploy

Production target: **Render + cloud MySQL** (not Vercel — Django monolith).

Full guide: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## Health check

```
GET /health/
```

Use for uptime monitoring (e.g. Google Apps Script ping).

---

## License / academic use

Built for DBMS coursework and viva demonstration.
