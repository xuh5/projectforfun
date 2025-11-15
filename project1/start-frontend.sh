#!/bin/bash
# Startup script for frontend server (macOS/Linux)
# This script checks dependencies and starts the Next.js dev server

set -e

echo "Starting Frontend Server..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "[WARNING] Dependencies not installed. Installing..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies!"
        exit 1
    fi
    cd ..
fi

# Check if package.json exists
if [ ! -f "frontend/package.json" ]; then
    echo "[ERROR] Frontend directory not found or invalid!"
    exit 1
fi

echo "Starting Next.js development server..."
echo ""
echo "Frontend will be available at http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
npm run dev

