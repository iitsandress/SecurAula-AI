#!/bin/bash

echo ""
echo "========================================"
echo " EduMon Agent - Quick Start"
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

echo "Checking configuration..."
if [ ! -f config.json ]; then
    echo "ERROR: config.json not found!"
    echo "Please run update_config.sh first to configure the agent."
    echo ""
    read -p "Press Enter to continue..."
    exit 1
fi

echo "Starting EduMon Agent (Simple Version)..."
echo ""
echo "Press Ctrl+C to stop the agent"
echo ""

python3 main_simple.py

echo ""
echo "Agent stopped."
read -p "Press Enter to continue..."