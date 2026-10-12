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
BIND_ARGS="--bind 0.0.0.0:8080 --bind 0.0.0.0:8000"
if [ -n "$PORT" ] && [ "$PORT" != "8080" ] && [ "$PORT" != "8000" ]; then
    BIND_ARGS="$BIND_ARGS --bind 0.0.0.0:${PORT}"
fi
exec gunicorn bph_project.wsgi:application ${BIND_ARGS} --workers 2 --timeout 120
