#!/bin/bash

echo "=============================================="
echo "  Running AI Video Generator Tests"
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
echo ""

# Run tests
echo "Running all tests..."
echo ""
python tests/run_tests.py

# Capture exit code
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Some tests failed!"
fi

exit $exit_code
