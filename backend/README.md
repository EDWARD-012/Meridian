# Meridian Backend

Django application root. All commands run from this folder.

## Quick start

```powershell
pip install -r requirements.txt
copy .env.example .env
$env:USE_SQLITE="True"
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Documentation

Full docs are in the project root:

- [../README.md](../README.md) — main overview
- [../docs/](../docs/) — schema, MySQL, SQL scripts, deploy, viva

## Key paths

| Path | Purpose |
|------|---------|
| `config/settings.py` | Database & security config |
| `sql_scripts/` | Raw SQL for viva |
| `shop/views.py` | All storefront pages |
| `templates/` | HTML |
| `static/` | CSS, JS, product images |
