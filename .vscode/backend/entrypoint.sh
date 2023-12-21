#!/bin/bash

set -x

python manage.py migrate --noinput || exit 1
python manage.py collectstatic --noinput || exit 1
cp -r /app/static/. /backend_static/ || exit 1
cp -r /app/media/. /backend_media/ || exit 1
python manage.py importcsv
gunicorn foodgram.wsgi:application --bind 0:8000

exec "$@"