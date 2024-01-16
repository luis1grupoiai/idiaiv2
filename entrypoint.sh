#!/bin/sh

echo 'Running collecstatic...'
python manage.py collectstatic --noinput --verbosity 2 --settings=config.settings.production

echo 'Applying migrations...'
python manage.py wait_for_db --settings=config.settings.production
python manage.py migrate --settings=config.settings.production

echo 'Waiting for Nginx to start...'
sleep 5

echo 'Running server...'
gunicorn -w 3 -t 120 --env DJANGO_SETTINGS_MODULE=config.settings.production config.wsgi:application --bind 0.0.0.0:333


