#!/bin/sh

# echo 'Running collecstatic...'
# python manage.py collectstatic --noinput --verbosity 2 --settings=config.settings.production

echo 'Applying migrations...'
python manage.py wait_for_db --settings=config.settings.production
python manage.py migrate --settings=config.settings.production

echo 'Running server...'
gunicorn --env DJANGO_SETTINGS_MODULE=config.settings.production config.wsgi:application -c gunicorn_config.py

echo 'Starting Nginx...'
nginx -g 'daemon off;'
sleep 5
echo 'Nginx started successfully.'