#!/bin/bash

# Try python3 first, fall back to python if not found
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

$PYTHON_CMD -m venv venv
source venv/bin/activate
pip install -r requirements.txt