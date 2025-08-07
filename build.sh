#!/usr/bin/env bash

# Install dependencies
pip install -r requirements.txt

# Run collectstatic and migrations
python manage.py collectstatic --noinput
python manage.py migrate
