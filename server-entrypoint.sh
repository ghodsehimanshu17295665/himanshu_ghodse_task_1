#!/bin/bash
/wait-for-it.sh db:5432 --timeout=30 --strict -- echo "Database is up!"

# Apply database migrations
python manage.py migrate

# Start the Django development server
python manage.py runserver 0.0.0.0:8000
