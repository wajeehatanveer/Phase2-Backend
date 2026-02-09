#!/bin/sh

# Exit on any error
set -e

echo "Starting backend deployment..."

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo "Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD=python3
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD=python
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
if [ -d "venv" ]; then
    . venv/bin/activate
elif [ -d ".venv" ]; then
    . .venv/bin/activate
fi

# Upgrade pip
$PYTHON_CMD -m pip install --upgrade pip

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
    exit 1
fi

# Make sure the environment variables are set
if [ -f ".env" ]; then
    echo "Loading environment variables..."
    # shellcheck disable=SC2046
    export $(grep -v '^#' .env | xargs)
fi

# Start the FastAPI application using uvicorn
echo "Starting FastAPI application..."
exec $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"