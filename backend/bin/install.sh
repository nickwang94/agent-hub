#!/bin/bash
# Install backend dependencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "============================================================"
echo "Installing Backend Dependencies"
echo "============================================================"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "Installing dependencies..."
pip install -e .

echo "============================================================"
echo "Installation complete!"
echo "Run: ./backend/bin/start.sh to start the server"
echo "============================================================"
