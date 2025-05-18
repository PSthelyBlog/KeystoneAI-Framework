# KeystoneAI Framework Quickstart Guide

This guide will help you get started with the KeystoneAI Framework quickly.

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key (required)
- Anthropic API key (optional)

## Available Utility Scripts

The framework includes several utility scripts to help you run and maintain it:

- `start_framework.sh`: Main script to start the framework
- `restart_clean.sh`: Reset and restart the framework with a clean state
- `clear_chat_history.sh`: Clear temporary files and chat history
- `install_links.sh`: Create symbolic links to run the framework from another directory
- `diagnose_framework.py`: Diagnose framework configuration issues
- `check_api_key.py`: Verify API key settings
- `debug_personas.py`: Debug persona loading issues

For more details on these scripts, see `UTILITY_SCRIPTS.md`.

## Setup

1. **Configure API keys**

   Set up your Gemini API key as an environment variable:

   ```bash
   export GEMINI_API_KEY=your_gemini_api_key_here
   ```

   If you plan to use Anthropic Claude (when supported):

   ```bash
   export ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Framework

### From the Main Directory

Use the included startup script:

```bash
./start_framework.sh
```

This script will:
- Check if your API keys are set correctly
- Start the framework with the default configuration

### From Any Directory

You can install symbolic links to run the framework from any directory:

```bash
# Run this from the main KeystoneAI-Framework directory
./install_links.sh [target_directory]
```

Examples:

```bash
# Link to current directory
./install_links.sh

# Link to a specific directory
./install_links.sh ./my_project

# Link to the example project
./install_links.sh ./example-project
```

Then you can run the framework from the target directory:

```bash
cd [target_directory]
./start_framework.sh
```

## Using the Framework

### Basic Commands

- `/help` - Display available commands
- `/persona <id>` - Switch between personas (e.g., `/persona forge`, `/persona catalyst`)
- `/clear` - Clear the conversation history
- `/quit` or `/exit` - Exit the application

### Understanding Personas

The framework includes two main personas:

1. **Catalyst** - The strategic AI lead focused on planning and architecture
2. **Forge** - The implementation specialist focused on coding and system operations

Switch between these personas using the `/persona` command.

### Configuration

The main configuration files are in the `config/` directory:

- `config.yaml` - General framework settings
- `FRAMEWORK_CONTEXT.md` - Context definition referencing personas, standards, and workflows

### Troubleshooting

If you encounter the error "Invalid input: 'content' argument must not be empty":
- Ensure you've set your GEMINI_API_KEY environment variable
- Try sending a message before using the `/persona` command
- Restart the framework with a clean state using the clear_chat_history.sh script

If the persona switching doesn't completely change the AI's behavior:
- After using `/persona forge` or `/persona catalyst`, send a new message to see the updated persona behavior
- If the AI still responds as the wrong persona, use the clear_chat_history.sh script and restart
- You can also use `/clear` to reset the conversation history while keeping the active persona

## Advanced Usage

### Using a Custom Configuration

```bash
python run_framework.py --config /path/to/your/config.yaml
```

### Enabling Debug Mode

```bash
python run_framework.py --log-level DEBUG
```

### Using a Different LLM Provider

```bash
python run_framework.py --llm-provider gemini
```

## Next Steps

Refer to the documents in `docs/` for more detailed information on the framework architecture and components.