#!/bin/bash
# Startup script for backend server (macOS/Linux)
# This script activates the virtual environment and starts the FastAPI server

set -e

echo "Starting Backend Server..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "backend/venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run the setup first:"
    echo "  cd backend"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if requirements are installed
if [ ! -f "backend/venv/bin/uvicorn" ]; then
    echo "[WARNING] Dependencies may not be installed."
    echo "Installing dependencies..."
    source backend/venv/bin/activate
    pip install -r backend/requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies!"
        exit 1
    fi
fi

# Activate venv
echo "Activating virtual environment..."
source backend/venv/bin/activate

echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run uvicorn from current directory (project1/) so it can find the backend package
python -m uvicorn backend.main:app --reload --port 8000

