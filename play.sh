#!/usr/bin/env bash
# PongWithIssues — Double-click launcher for Linux/macOS
# Just run: ./play.sh  (or double-click in file manager)

cd "$(dirname "$0")"

# Find python3 or python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Error: Python not found. Install Python 3.8+ from https://python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

$PYTHON play.py
