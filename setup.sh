#!/bin/sh

# initializes a virtual environment
# and installs required dependencies
if [ ! -d "env" ]; then
    python3 -m venv venv
fi
. venv/bin/activate
pip install -r requirements.txt
