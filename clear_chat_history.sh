#!/bin/bash
# Script to clear temporary files and chat history from the KeystoneAI Framework

# Determine the absolute path to the KeystoneAI Framework directory
# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Clearing temporary files and chat history..."
cd "$SCRIPT_DIR" # Change to framework directory to ensure correct paths

# Find and remove temporary files associated with the framework
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} +

# Optional: Reset the framework log
if [ -f "framework.log" ]; then
    echo "Resetting framework.log"
    > framework.log
fi

# Clear any cached state 
if [ -f "maia_project_state.json" ]; then
    echo "Removing maia_project_state.json"
    rm maia_project_state.json
fi

echo "Done! Framework state has been reset."
echo "Use ./start_framework.sh to start a fresh session."