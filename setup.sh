#!/bin/bash

set -e

echo "Setting up Mycel..."

if [ ! -d "env" ]; then
    python3 -m venv env
    echo "Virtual environment created."
fi

echo "Installing dependencies..."
./env/bin/pip install --upgrade pip
./env/bin/pip install -r requirements.txt

echo "==> Setting up Node dependencies..."
./install_node_deps.sh

if [ ! -f "config.json" ]; then
    echo "Creating configuration file..."
    cp config.json.example config.json
else
    echo "config.json already exists. Your settings have been preserved."
fi

echo "Setup complete! Use ./run.sh to start the application."
