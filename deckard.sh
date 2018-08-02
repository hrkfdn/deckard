#!/bin/sh

# initializes a virtual environment
# and installs required dependencies
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment was not found. Please run 'setup.sh' first"
    exit 1
fi

source venv/bin/activate
python3 src/deckard.py $@
