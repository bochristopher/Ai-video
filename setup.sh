#!/bin/bash

echo "=============================================="
echo "  AI Video Generator - Setup Script"
echo "=============================================="
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Create virtual environment
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "[4/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Set up environment file
echo "[5/5] Setting up environment file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from .env.example"
    echo ""
    echo "⚠ IMPORTANT: Please edit .env and add your API keys!"
    echo "   - REPLICATE_API_TOKEN (required)"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p videos
mkdir -p logs
echo "✓ Directories created"
echo ""

echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: python backend/app.py"
echo "  4. Open: http://localhost:5000"
echo ""
echo "To run tests:"
echo "  python tests/run_tests.py"
echo ""
echo "=============================================="
