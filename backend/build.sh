#!/bin/bash
# Post-deploy setup (run manually once against cloud DB — NOT on every Render build)
set -e
python manage.py migrate --noinput
# Seed demo data only for local/viva — skip in production:
# python manage.py seed_data
