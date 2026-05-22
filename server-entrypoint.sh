#!/bin/sh

set -e

echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Postgres not ready... retrying"
  sleep 2
done

echo "PostgreSQL is up!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."

# PRODUCTION server (better than runserver)
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000