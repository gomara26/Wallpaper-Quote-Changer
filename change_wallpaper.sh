#!/bin/bash

# Mac Wallpaper Quote Changer - Shell Script
# This script runs the Python wallpaper changer

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the Python script
python3 wallpaper_changer.py

# If there was an error, keep the terminal open (useful for debugging)
if [ $? -ne 0 ]; then
    echo "Press Enter to exit..."
    read
fi


