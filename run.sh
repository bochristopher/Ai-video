#!/bin/bash

echo "=============================================="
echo "  Starting AI Video Generator"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "✗ Virtual environment not found!"
    echo "Please run setup.sh first:"
    echo "  ./setup.sh"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠ WARNING: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠ Please edit .env and add your API keys before running!"
    echo "Press Ctrl+C to exit and edit .env, or Enter to continue anyway..."
    read
fi

# Start the server
echo "Starting server..."
echo ""
python backend/app.py
