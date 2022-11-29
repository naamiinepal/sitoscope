#!/bin/sh

set -e
. .venv/bin/activate
echo "Starting Django..."
python manage.py runserver 0.0.0.0:23232
