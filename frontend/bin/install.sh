#!/bin/bash
# Install frontend dependencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "============================================================"
echo "Installing Frontend Dependencies"
echo "============================================================"

npm install

echo "============================================================"
echo "Installation complete!"
echo "Run: ./frontend/bin/start.sh to start the server"
echo "============================================================"
