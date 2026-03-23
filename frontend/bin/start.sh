#!/bin/bash
# Start frontend development server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "============================================================"
echo "Agent Hub - Frontend Server"
echo "============================================================"

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Starting frontend development server..."
echo "Visit http://localhost:5173"
echo "============================================================"

npm run dev
