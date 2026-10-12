#!/bin/sh
set -e

echo "=== Menjalankan Database Migrations ke Supabase ==="
python manage.py migrate --noinput

# Jika variabel LOAD_INITIAL_DATA di-set ke 'true', import data awal
if [ "$LOAD_INITIAL_DATA" = "true" ]; then
    echo "=== Mengimpor data awal (datadump.json) ==="
    python manage.py loaddata datadump.json || true
fi

echo "=== Menjalankan Web Server Gunicorn ==="
exec gunicorn bph_project.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
