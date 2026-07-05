#!/bin/bash
set -e
 
cd "$(dirname "$0")"
 
echo "==> Pulling latest changes..."
git pull
 
echo "==> Installing/updating dependencies..."
./env/bin/pip install -r requirements.txt
 
echo "==> Update complete."
echo "If this update introduced new config options, check config.example.json"
echo "and update your config.json accordingly."
echo ""
echo "Restart Mycel with: ./run.sh"
 
