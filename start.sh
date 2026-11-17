#!/usr/bin/env bash
# Comando de inicialização usado pelo Render.
# O disco do plano gratuito é apagado a cada deploy ou reinício, então o
# banco SQLite é recriado e preenchido com os dados de exemplo toda vez.
set -o errexit
export PYTHONUNBUFFERED=1

python manage.py migrate --noinput
python manage.py loaddata seed

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" || true
  # Os posts de exemplo não têm autor; ficam com o superusuário.
  python manage.py shell -c "import os
from django.contrib.auth import get_user_model
from blog.models import Post
user = get_user_model().objects.get(username=os.environ['DJANGO_SUPERUSER_USERNAME'])
Post.objects.filter(author=None).update(author=user)
print('Superusuário com e-mail:', bool(user.email), '| senha utilizável:', user.has_usable_password())"
fi

python manage.py shell -c "from django.conf import settings
print('Backend de e-mail:', settings.EMAIL_BACKEND)"

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}"
