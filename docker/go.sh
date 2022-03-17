#!/usr/bin/env sh

cd /opt/aweber

pip install -r requirements.txt

python manage.py runserver 0.0.0.0:9000