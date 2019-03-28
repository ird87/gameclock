#!/bin/bash
set -ex

#python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
daphne ChessClockAPI.asgi:application --port 8000 --bind 0.0.0.0

