#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../.."

PY=./python_modules/bin/python
PIP=./python_modules/bin/pip

if [ "$#" -gt 0 ]; then
    $PIP install "$@"
elif [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    cat requirements.txt | grep -Eo '(^[^#]+)' | xargs -n 1 $PIP install
fi

$PIP freeze > requirements.txt
