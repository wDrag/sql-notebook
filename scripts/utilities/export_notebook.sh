#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../.."

INPUT="$1"
OUTPUT="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: pdf.sh <input.ipynb> <output.pdf>"
    exit 1
fi

./python_modules/bin/python scripts/utilities/export_notebook.py "$INPUT" "$OUTPUT"