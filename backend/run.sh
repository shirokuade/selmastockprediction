#!/bin/bash

# Run script for Stock Prediction Backend

echo "=============================================="
echo "Indonesian Stock Prediction API"
echo "=============================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found."
    echo "Creating new virtual environment..."

    # Try to find Python 3.12 or 3.11
    if command -v python3.12 &> /dev/null; then
        echo "Using Python 3.12"
        python3.12 -m venv venv
    elif command -v python3.11 &> /dev/null; then
        echo "Using Python 3.11"
        python3.11 -m venv venv
    else
        echo "Using default Python 3"
        python3 -m venv venv
    fi

    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi

    echo "✅ Virtual environment created"
fi

# Activate virtual environment using explicit path
echo "Activating virtual environment..."
source venv/bin/activate

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"
echo ""

# Show Python version
echo "Python version:"
python --version
echo ""

# Install dependencies
echo "Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies from requirements.txt..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi

    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data qlib_data models logs user_settings
echo "✅ Directories created"
echo ""

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your configuration"
    echo ""
fi

# Run diagnostic
echo "Running environment diagnostic..."
python check_env.py
echo ""

# Run the application
echo "=============================================="
echo "Starting FastAPI server..."
echo "=============================================="
echo ""
echo "API will be available at: http://localhost:8000"
echo "Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Use explicit python from venv
exec python main.py
