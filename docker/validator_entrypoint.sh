#!/usr/bin/env bash

set -e

mkdir -p /app/logs

echo "Apply database migrations."
python manage.py migrate --noinput

echo "Start Gunicorn."
# in the production instance, the workers must be controlled
# otherwise, gunicorn can overconsume the CPU and other processes can be in hunger.
exec gunicorn email_validator_local.wsgi:application --bind 0.0.0.0:${PORT} --workers 3