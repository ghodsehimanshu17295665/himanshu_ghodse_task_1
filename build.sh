#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Wait for PostgreSQL
if [[ -z "$CI" ]]; then
  echo "-> Waiting for PostgreSQL to be ready"
  export PGPASSWORD="${DATABASE_URL##*:}"
  until pg_isready -h "${DATABASE_URL##*@}" -p 5432; do
    echo "-> Database not ready - retrying in 5s"
    sleep 5
  done
fi

python manage.py collectstatic --noinput
python manage.py migrate