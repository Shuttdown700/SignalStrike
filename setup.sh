#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if Python is installed and display the version
if ! command -v python3 &>/dev/null; then
    echo "Python is not installed or not found in PATH. Please install Python and try again."
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    echo "Python is installed. Version: $PYTHON_VERSION"
fi

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    # Create virtual environment
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
source venv/bin/activate
echo "Virtual environment activated."

# Upgrade pip
python -m pip install --upgrade pip
echo "Pip upgraded."

# Install required Python modules if requirements.txt exists
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt
    echo "Required modules installed."
else
    echo "requirements.txt not found. Skipping module installation."
fi

echo "Virtual environment setup complete!"
