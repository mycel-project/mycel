#!/bin/bash
set -e
 
cd "$(dirname "$0")/.."
 
echo "==> Pulling latest changes..."
git pull
 
echo "==> Installing/updating dependencies..."
./env/bin/pip install -r requirements.txt

echo "==> Setting up Node dependencies..."
./scripts/install_node_deps.sh
 
echo "==> Checking config.json for new options..."
./env/bin/python3 scripts/merge_config.py
 
echo "==> Update complete."
echo "Restart Mycel with: ./mycel.sh run"
 
