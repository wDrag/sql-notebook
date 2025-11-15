#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../.."

# Use venv python explicitly
./python_modules/bin/python main.py
