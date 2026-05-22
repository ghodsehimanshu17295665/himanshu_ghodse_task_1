#!/bin/sh

set -e

echo "Starting Django without blocking DB wait..."

python manage.py migrate

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000

# #!/bin/sh

# set -e

# echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."

# while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
#   echo "Postgres not ready... retrying"
#   sleep 1
# done

# echo "PostgreSQL started"

# python manage.py migrate

# echo "Starting Django server..."
# python manage.py runserver 0.0.0.0:8000
