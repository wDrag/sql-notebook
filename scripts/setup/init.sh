#!/usr/bin/env bash
set -e

# Keep your original cd
cd "$(dirname "$0")/../.."

# Create venv if it doesn't exist
if [ ! -d "python_modules" ]; then
    python -m venv python_modules
fi

# Use venv python directly (no activation required)
./python_modules/bin/python -m pip install --upgrade pip

echo "Init complete. Virtual environment located at ./python_modules"
