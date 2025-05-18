#!/bin/bash
# Wrapper script to run the KeystoneAI Framework

# Determine the absolute path to the KeystoneAI Framework directory
# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Execute the API key check script with absolute path
python3 "$SCRIPT_DIR/check_api_key.py"
if [ $? -ne 0 ]; then
    echo "API key check failed. Please set the required environment variables."
    exit 1
fi

# Run the framework with absolute paths
echo "Starting KeystoneAI Framework..."
chmod +x "$SCRIPT_DIR/run_fixed.py"
cd "$SCRIPT_DIR" # Change to framework directory to ensure correct relative paths
python3 "$SCRIPT_DIR/run_fixed.py"

# Exit with the same status as the framework
exit $?