#!/bin/bash
# Start Agent Hub Backend Server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "============================================================"
echo "Agent Hub - Backend Server"
echo "============================================================"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -e ."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found, please configure API Key"
    echo "Copy .env.example to .env and update it"
fi

echo "Starting API server..."
echo "API will run at http://localhost:8080"
echo "============================================================"

python3 backend/api.py
