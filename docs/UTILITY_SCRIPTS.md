# KeystoneAI Framework Utility Scripts

This document explains the utility scripts available to help you run, maintain, and troubleshoot the KeystoneAI Framework.

## Quick Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `start_framework.sh` | Run the framework | `./start_framework.sh` |
| `restart_clean.sh` | Reset and restart | `./restart_clean.sh` |
| `clear_chat_history.sh` | Clear temporary files | `./clear_chat_history.sh` |
| `install_links.sh` | Install scripts in another directory | `./install_links.sh [target_dir]` |
| `diagnose_framework.py` | Diagnose setup issues | `python diagnose_framework.py` |
| `check_api_key.py` | Verify API key settings | `python check_api_key.py` |
| `debug_personas.py` | Debug persona loading | `python debug_personas.py` |

## Detailed Description

### `start_framework.sh`

The main script to start the KeystoneAI Framework.

**Features:**
- Verifies Python is installed
- Checks required API keys
- Runs the framework with the correct configuration

**Usage:**
```bash
./start_framework.sh
```

### `restart_clean.sh`

Completely resets and restarts the framework with a clean state.

**Features:**
- Stops any running framework instances
- Clears all temporary files and cached state
- Verifies configuration is in place
- Checks API key is set
- Restarts the framework

**Usage:**
```bash
./restart_clean.sh
```

### `clear_chat_history.sh`

Clears temporary files and chat history without restarting the framework.

**Features:**
- Removes Python cache files
- Resets framework logs
- Clears any cached state

**Usage:**
```bash
./clear_chat_history.sh
```

### `install_links.sh`

Creates symbolic links to the framework scripts in another directory to run the framework from there.

**Features:**
- Creates links to all utility scripts
- Works with absolute or relative paths
- Can create the target directory if it doesn't exist

**Usage:**
```bash
# Link to current directory
./install_links.sh

# Link to a specific directory
./install_links.sh ./my_project

# Link to an absolute path
./install_links.sh /home/user/projects/my_keystone_project
```

### `diagnose_framework.py`

Comprehensive diagnostic tool that analyzes framework configuration and highlights issues.

**Features:**
- Checks configuration files
- Validates API key settings
- Verifies persona definitions
- Tests message initialization

**Usage:**
```bash
python diagnose_framework.py
```

### `check_api_key.py`

Utility to check if required API keys are properly set in the environment.

**Features:**
- Checks for required Gemini API key
- Validates optional API keys (Anthropic, Azure)
- Shows masked key values for security

**Usage:**
```bash
python check_api_key.py
```

### `debug_personas.py`

Tool to debug persona detection and loading issues.

**Features:**
- Shows loaded documents
- Lists available personas
- Verifies section detection
- Helps troubleshoot persona switching

**Usage:**
```bash
python debug_personas.py
```

## Common Troubleshooting Scenarios

### 1. Persona Switching Not Working

If `/persona forge` or `/persona catalyst` commands don't work:

```bash
# First, diagnose the issue
python diagnose_framework.py

# Then, restart with a clean state
./restart_clean.sh
```

### 2. API Key Issues

If you encounter API-related errors:

```bash
# Check if your keys are properly set
python check_api_key.py

# Set your API key if needed
export GEMINI_API_KEY=your_key_here
```

### 3. Running from Another Directory

To run the framework from a different directory:

```bash
# Install links to your target directory
cd /path/to/KeystoneAI-Framework
./install_links.sh /path/to/target/directory

# Go to the target directory and run
cd /path/to/target/directory
./start_framework.sh
```

## Advanced Usage

### Setting Custom Environment Variables

You can set custom environment variables before starting the framework:

```bash
export PROJECT_DIR="$(pwd)"
export GEMINI_API_KEY=your_key
./start_framework.sh
```

### Debugging the Framework Startup

For more verbose output during startup:

```bash
python run_fixed.py --log-level DEBUG
```