#!/bin/bash

# Ensure pip is installed
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user

# Upgrade pip to the latest version
python3 -m pip install --upgrade pip --user

# Install requirements
python3 -m pip install -r requirements.txt --user

# Run Django management commands
python3 manage.py collectstatic --noinput
python3 manage.py migrate
