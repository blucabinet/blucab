#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    echo "Superuser-Credentials given. Start creating superuser:"
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

$@