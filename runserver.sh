#!/bin/sh

set -e
. .venv/bin/activate
echo "Starting Django..."
gunicorn
