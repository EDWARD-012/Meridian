# Deployment Guide (Render + MySQL)

Step-by-step deploy for production. **Use Render, not Vercel** — this is a Django WSGI app.

---

## Prerequisites

- GitHub repo with this project
- [Render](https://render.com) account (free tier OK)
- Cloud MySQL (Render PostgreSQL nahi — project MySQL ke liye configured hai)

**MySQL providers (free/cheap):**
- [Railway](https://railway.app) MySQL
- [PlanetScale](https://planetscale.com) (MySQL compatible)
- [Aiven](https://aiven.io) free trial

---

## Step 1 — Push code to GitHub

```powershell
git add .
git commit -m "Prepare for Render deploy"
git push origin main
```

---

## Step 2 — Create MySQL database (cloud)

Example (Railway):

1. New Project → Add MySQL
2. Copy **connection URL**, e.g.:
   ```
   mysql://root:PASSWORD@containers-us-west-xxx.railway.app:3306/railway
   ```
3. Note: database name, user, password, host, port

---

## Step 3 — Deploy on Render

### Option A — Blueprint (`render.yaml` already in repo)

1. Render Dashboard → **New** → **Blueprint**
2. Connect GitHub repo
3. Render reads `render.yaml` automatically

### Option B — Manual Web Service

1. **New Web Service** → connect repo
2. Settings:
   - **Root Directory:** `backend`
   - **Build Command:**
     ```
     pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```
     gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
     ```

---

## Step 4 — Environment variables (Render)

| Key | Value | Required |
|-----|-------|----------|
| `SECRET_KEY` | Long random string (50+ chars) | Yes |
| `DEBUG` | `False` | Yes |
| `USE_SQLITE` | `False` | Yes |
| `DATABASE_URL` | `mysql://user:pass@host:3306/dbname` | Yes |
| `ALLOWED_HOSTS` | `your-app.onrender.com,.onrender.com` | Yes |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.onrender.com` | Yes |
| `SECURE_SSL_REDIRECT` | `True` | Yes |

> App **will not start** if `DEBUG=False` without `SECRET_KEY`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.

Update `render.yaml` mein `CSRF_TRUSTED_ORIGINS` apne actual app URL se match karo.

---

## Step 5 — First deploy

1. Click **Deploy**
2. Build logs mein dekho:
   - `migrate` success
   - `collectstatic` success
3. Open `https://your-app.onrender.com/health/` → should return `{"status":"ok"}`

---

## Step 6 — Seed demo data (one time)

Render Shell (or local with production `DATABASE_URL`):

```bash
python manage.py seed_data
```

Creates:
- User `demo` / `demo1234` (staff)
- 48 products, categories, reviews

---

## Step 7 — Cron job (optional)

`render.yaml` includes hourly cron:

```
python manage.py cancel_stale_orders
```

Cancels unpaid Razorpay orders after 60 minutes and restores stock.

---

## Step 8 — MySQL views (viva on production)

Shell se ya local machine se production DB par:

```bash
mysql -h HOST -u USER -p DATABASE < sql_scripts/views.sql
```

---

## Post-deploy checklist

- [ ] Homepage loads
- [ ] Login works (`demo` / `demo1234`)
- [ ] Add to cart → checkout → Razorpay demo
- [ ] `/db-insights/` opens (staff only)
- [ ] `/health/` returns OK
- [ ] HTTPS works (no CSRF 403 on POST)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `DisallowedHost` | Fix `ALLOWED_HOSTS` |
| CSRF 403 on login | Add `CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com` |
| `ImproperlyConfigured SECRET_KEY` | Set unique `SECRET_KEY` |
| Static files 404 | Run `collectstatic` in build |
| DB connection error | Check `DATABASE_URL`, allow Render IP on MySQL host |
| Empty site | Run `seed_data` |

---

## Keep-alive (free tier sleep)

Render free tier sleeps after inactivity. Use uptime ping on `/health/`:

See `docs/google-apps-script-ping.js` if present, or use UptimeRobot.

---

## See also

- [MYSQL_SETUP.md](MYSQL_SETUP.md) — local MySQL for development
- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) — dev commands
