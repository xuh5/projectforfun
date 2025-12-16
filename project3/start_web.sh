#!/bin/bash
echo "Starting project3 web server..."
cd "$(dirname "$0")"
source venv/bin/activate
python -m src.main serve

