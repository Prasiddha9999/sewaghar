#!/bin/bash

# Ensure Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 not found, installing Python3"
    apt-get update && apt-get install -y python3
fi

# Ensure pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "pip3 not found, installing pip3"
    apt-get install -y python3-pip
fi

# Install requirements
pip3 install -r requirements.txt

# Run Django management commands (if needed)
python3 manage.py collectstatic --noinput
python3 manage.py migrate
