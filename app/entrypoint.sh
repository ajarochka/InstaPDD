#!/bin/bash

source /venv/bin/activate

python manage.py collectstatic --noinput

# Apply database migrations
python manage.py makemigrations
until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done

# Start server
supervisord -c /app/service.conf
