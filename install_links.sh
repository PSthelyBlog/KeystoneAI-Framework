#!/bin/bash
# Script to create symbolic links to KeystoneAI Framework scripts in a user-specified directory

# Determine the absolute path to the KeystoneAI Framework directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Display usage if needed
function show_usage {
    echo "Usage: $0 [target_directory]"
    echo "If no directory is specified, links will be created in the current directory."
    echo "Examples:"
    echo "  $0             # Creates links in the current directory"
    echo "  $0 ./myproject # Creates links in ./myproject"
    echo "  $0 /path/to/dir # Creates links in /path/to/dir"
}

# Parse arguments
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_usage
    exit 0
fi

# Determine target directory (default to current directory if not specified)
if [ -z "$1" ]; then
    TARGET_DIR="$(pwd)"
    echo "No target directory specified. Using current directory: $TARGET_DIR"
else
    # Convert relative path to absolute path
    if [[ "$1" == /* ]]; then
        # Absolute path
        TARGET_DIR="$1"
    else
        # Relative path
        TARGET_DIR="$(pwd)/$1"
    fi
    echo "Using target directory: $TARGET_DIR"
fi

# Check if the target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Target directory not found at $TARGET_DIR"
    echo "Would you like to create it? [y/N]"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        mkdir -p "$TARGET_DIR"
        echo "Created directory $TARGET_DIR"
    else
        echo "Aborting installation."
        exit 1
    fi
fi

echo "Creating symbolic links to KeystoneAI Framework scripts..."

# Create symbolic links for the main scripts
ln -sf "$SCRIPT_DIR/start_framework.sh" "$TARGET_DIR/start_framework.sh"
ln -sf "$SCRIPT_DIR/restart_clean.sh" "$TARGET_DIR/restart_clean.sh"
ln -sf "$SCRIPT_DIR/clear_chat_history.sh" "$TARGET_DIR/clear_chat_history.sh"
ln -sf "$SCRIPT_DIR/check_api_key.py" "$TARGET_DIR/check_api_key.py"
ln -sf "$SCRIPT_DIR/run_fixed.py" "$TARGET_DIR/run_fixed.py"
ln -sf "$SCRIPT_DIR/diagnose_framework.py" "$TARGET_DIR/diagnose_framework.py"

echo "Symbolic links created successfully in $TARGET_DIR"
echo "You can now run the framework from this directory:"
echo "  cd $(realpath --relative-to="$(pwd)" "$TARGET_DIR")"
echo "  ./start_framework.sh"