#!/bin/bash

echo ""
echo "========================================"
echo " EduMon Agent - Configuration Update"
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

python3 update_config.py

echo ""
read -p "Press Enter to continue..."