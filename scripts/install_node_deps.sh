#!/bin/bash
# Installs Node.js (via nodeenv, inside the Python venv) and npm dependencies
# (e.g. Defuddle) needed by Mycel. Safe to run multiple times (idempotent).
set -e
 
cd "$(dirname "$0")/.."
 
# Install nodeenv into the Python venv if not already present
if ! ./env/bin/python -c "import nodeenv" 2>/dev/null; then
    echo "==> Installing nodeenv..."
    ./env/bin/pip install nodeenv
fi
 
# Install Node.js into the venv if not already present
if [ ! -f ./env/bin/node ]; then
    echo "==> Installing Node.js into the virtual environment..."
    ./env/bin/nodeenv -p
else
    echo "==> Node.js already installed, skipping."
fi
 
# Install/update npm dependencies (e.g. Defuddle), scoped to ./node_deps
echo "==> Installing Node dependencies (npm)..."
PATH="$(pwd)/env/bin:$PATH" ./env/bin/npm install --prefix ./node_deps
 
