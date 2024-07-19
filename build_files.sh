#!/bin/bash

# Install pip if it's not already installed
if ! command -v pip &> /dev/null
then
    echo "pip not found, installing pip"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py --user
fi

# Install requirements
pip install -r requirements.txt
python3.9 manage.py collectstatic