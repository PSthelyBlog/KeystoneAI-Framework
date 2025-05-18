#!/bin/bash
# Script to completely reset and restart the KeystoneAI Framework

# Determine the absolute path to the KeystoneAI Framework directory
# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Performing complete framework reset and restart..."
cd "$SCRIPT_DIR" # Change to framework directory to ensure correct paths

# Kill any running instances of the framework
echo "Stopping any running framework instances..."
pkill -f "python3 run_framework.py" &>/dev/null
pkill -f "python3 run_fixed.py" &>/dev/null

# Clear all temporary files and state
echo "Clearing all temporary files and state..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
[ -f "framework.log" ] && > framework.log
[ -f "maia_project_state.json" ] && rm maia_project_state.json

# Verify config files
echo "Verifying configuration..."
if [ ! -f "config/config.yaml" ]; then
    echo "Creating config.yaml from example..."
    cp config/config.yaml.example config/config.yaml
fi

if [ ! -f "config/FRAMEWORK_CONTEXT.md" ]; then
    echo "Creating FRAMEWORK_CONTEXT.md from example..."
    cp config/FRAMEWORK_CONTEXT.md.example config/FRAMEWORK_CONTEXT.md
    # Ensure initial prompt is uncommented
    sed -i 's/# initial_prompt_template:/initial_prompt_template:/' config/FRAMEWORK_CONTEXT.md
fi

# Verify API key
echo "Checking API key..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "ERROR: GEMINI_API_KEY is not set!"
    echo "Please set it with: export GEMINI_API_KEY=your_key_here"
    exit 1
fi

# Start framework with fresh state
echo "Starting framework with clean state..."
python3 run_fixed.py