#!/bin/sh
set -e

echo "Start Migrations"
python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable
echo "---------------------"


if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    echo "Superuser-Credentials given. Start creating superuser:"
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
    echo "---------------------"
fi

echo "Compile Translations"
python manage.py compilemessages
echo "---------------------"

echo "Entrypoint Done"
echo "Start Server"
$@
