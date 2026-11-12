#!/usr/bin/env bash
# Comando de inicialização usado pelo Render.
# O disco do plano gratuito é apagado a cada deploy ou reinício, então o
# banco SQLite é recriado e preenchido com os dados de exemplo toda vez.
set -o errexit

python manage.py migrate --noinput
python manage.py loaddata seed

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" || true
fi

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}"
