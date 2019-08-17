#!/bin/bash
set -e
set -o pipefail # if any code doesn't return 0, exit the script

function setup_server() {
  python manage.py makemigrations
  python manage.py migrate
  echo "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('devadmin', 'admin@example.com', 'nimda')" | python manage.py shell
}

function start_server() {
    echo Starting Django development server..
    python manage.py runserver 0.0.0.0:8000
}

setup_server
start_server

exit 0
