#!/bin/bash

# Check Python version
python3 --version

# Create and activate a virtual environment
workon sewa

# Install or upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Run Django management commands
python manage.py collectstatic --noinput
python manage.py migrate


