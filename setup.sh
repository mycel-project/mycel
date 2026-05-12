#!/bin/bash

# Exit on error
set -e

echo "Setting up Mycel backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "env" ]; then
    python3 -m venv env
    echo "Virtual environment created."
fi

# Install dependencies
echo "Installing dependencies..."
./env/bin/pip install --upgrade pip
./env/bin/pip install -r requirements.txt

echo "Setup complete! Use ./run.sh to start the application."
