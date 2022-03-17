#!/usr/bin/env bash

cd /opt/aweber

pip install -r requirements.txt

# django's secret key is necessary, but we won't use it, so no need for it to be consistent.
# github, however is very unhappy about leaving the secret in the settings file
export DJANGO_SECRET="$(python -c 'import secrets; print(secrets.token_hex(50))' |head -c 67)"

#python manage.py makemigrations
# schema changes are stored in VCS, so they can be controlled by commit
# if changes are there, they're expected to be applied
python manage.py migrate

python manage.py runserver 0.0.0.0:9000