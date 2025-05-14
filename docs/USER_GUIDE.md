# AI-Assisted Framework User Guide

**Version:** 2.0.0
**Date:** May 14, 2025

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [Basic Usage](#basic-usage)
   - [Starting the Framework](#starting-the-framework)
   - [Interacting with the Framework](#interacting-with-the-framework)
   - [Using Special Commands](#using-special-commands)
   - [Working with Tools](#working-with-tools)
6. [Configuration](#configuration)
   - [config.yaml](#configyaml)
   - [FRAMEWORK_CONTEXT.md](#framework_contextmd)
   - [Environment Variables](#environment-variables)
7. [Using MAIA-Workflows](#using-maia-workflows)
8. [Advanced Usage](#advanced-usage)
   - [Using Custom LLM Providers](#using-custom-llm-providers)
   - [Managing Conversation Context](#managing-conversation-context)
   - [Understanding the ICERC Protocol](#understanding-the-icerc-protocol)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## Introduction

The AI-Assisted Framework is a powerful, LLM-agnostic system that enables structured AI collaboration for software development and other projects. It features two primary AI personas:

- **Catalyst**: The visionary strategist, architect, and AI team lead
- **Forge**: The expert AI implementer and system operator

The framework is guided by "The AI-Assisted Dev Bible" standards and uses the MAIA-Workflow framework for structured collaboration. Version 2.0.0 introduces a completely redesigned LLM Agnostic Core Architecture (LACA) with three key components:

- **LIAL**: LLM Interaction Abstraction Layer
- **TEPS**: Tool Execution & Permission Service
- **DCM**: Dynamic Context Manager

This enables the framework to work with different LLM providers while maintaining a consistent user experience and robust security measures.

## Prerequisites

Before using the AI-Assisted Framework, you need:

1. **Python 3.8+**: The framework requires Python 3.8 or higher
2. **Git**: For cloning the repository and version control
3. **API Keys**: For LLM providers (Gemini, Anthropic, etc.)
4. **Bash-compatible Shell**: The framework is designed to run in a Bash-compatible environment

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PSthelyBlog/ai_assisted_framework_claude.git
cd ai_assisted_framework_claude
```

### 2. Create a Virtual Environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys

Create a `.env` file in the project root with your API keys:

```
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

Or set environment variables directly:

```bash
export GEMINI_API_KEY=your_gemini_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Getting Started

After installation, you need to:

1. **Create a Project Directory**: Either create a new directory or use an existing one
2. **Configure the Framework**: Copy and customize `config.yaml.example` to `config.yaml`
3. **Create Context Definition**: Copy and customize `FRAMEWORK_CONTEXT.md.example` to `FRAMEWORK_CONTEXT.md`
4. **Start the Framework**: Use the `run_framework.py` script to start the application

### Quick Start Example

```bash
# Create a new project directory
mkdir my_project
cd my_project

# Copy configuration examples
cp /path/to/ai_assisted_framework_claude/my_new_ai_project/config/config.yaml.example config.yaml
cp /path/to/ai_assisted_framework_claude/my_new_ai_project/config/FRAMEWORK_CONTEXT.md.example FRAMEWORK_CONTEXT.md

# Edit configuration files with your preferred editor
nano config.yaml
nano FRAMEWORK_CONTEXT.md

# Start the framework
python /path/to/ai_assisted_framework_claude/my_new_ai_project/run_framework.py --config ./config.yaml
```

## Basic Usage

### Starting the Framework

The primary way to start the framework is using the `run_framework.py` script:

```bash
python run_framework.py --config /path/to/config.yaml
```

Optional arguments:
- `--config`: Path to the configuration file (default: `config.yaml` in current directory)
- `--context`: Path to the context definition file (overrides config setting)
- `--verbose`: Enable verbose logging
- `--debug`: Enable debug mode

### Interacting with the Framework

Once the framework is running, you'll see a welcome message and a prompt. You can interact with the AI personas by typing your messages and pressing Enter.

```
Framework Core Application started. Type /help for available commands.

> Hello, I'd like to start a new project to build a website.

(Catalyst): I'd be happy to help you start a new website project. Before we begin, let's establish some basics about what you're looking to build. I'll guide this conversation using the MAIA-Workflow methodology to ensure a structured approach.

Could you tell me more about:
1. The purpose of the website
2. Your target audience
3. Any specific features you'd like to include
4. Your technical preferences (if any)
5. Your timeline for this project

This will help me define an appropriate MAIA-Workflow for your project.
```

### Using Special Commands

The framework supports several special commands that start with `/`:

| Command | Description |
|---------|-------------|
| `/help` | Show help message |
| `/quit` or `/exit` | Exit the application |
| `/clear` | Clear conversation history |
| `/system` | Add a system message |
| `/debug` | Toggle debug mode |

Examples:

```
> /help
Available commands:
/help - Show this help message
/quit - Exit the application
/exit - Exit the application
/clear - Clear conversation history
/system - Add a system message
/debug - Toggle debug mode

> /system You are focused on helping with Python development
Added system message: You are focused on helping with Python development

> /debug
Debug mode enabled
```

### Working with Tools

The framework includes several tools that the AI can use to assist you. When an AI requests to use a tool, TEPS will present you with an ICERC (Intent, Command, Expected Outcome, Risk Assessment, Confirmation) prompt to ensure safety.

Example:

```
(Forge): I'll create that Python file for you. Let me prepare the command to write the file.

Intent: Create a new Python file with a simple "Hello World" program
Command: Write file 'hello.py' with content: 'print("Hello, World!")'
Expected Outcome: A new file named hello.py will be created with the given content
Risk Assessment: Low. This operation only creates a new file in the current directory.
Please confirm [Y/N]: 
```

You can respond with `Y` to allow the tool execution or `N` to deny it. The result will be added to the conversation and the AI will continue with the appropriate response.

## Configuration

### config.yaml

The `config.yaml` file controls the behavior of the framework and its components. Here are the key sections:

#### General Settings

```yaml
framework:
  name: "AI-Assisted Framework"
  version: "2.0.0"
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_file: "framework.log"
```

#### LLM Provider Settings

```yaml
llm:
  provider: "gemini"  # Currently supported: gemini, anthropic (planned)
  gemini:
    api_key: "${GEMINI_API_KEY}"  # Environment variable reference
    model: "gemini-1.5-pro"
    temperature: 0.7
    max_output_tokens: 8192
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-opus-20240229"
    temperature: 0.7
    max_tokens: 4096
```

#### TEPS Settings

```yaml
teps:
  permission_required: true
  allowed_tools:
    - "file_read"
    - "file_write"
    - "web_search"
    - "bash"
  secure_mode: true
  tool_timeout: 30000  # milliseconds
```

#### Message History Settings

```yaml
message_history:
  max_length: 100
  pruning_strategy: "remove_oldest"  # remove_oldest, summarize (planned)
  prioritize_system_messages: true
```

#### DCM Settings

```yaml
dcm:
  context_definition_path: "${PROJECT_DIR}/FRAMEWORK_CONTEXT.md"
  max_document_size: 10485760  # 10MB
```

### FRAMEWORK_CONTEXT.md

The `FRAMEWORK_CONTEXT.md` file defines the context for the framework, including system prompts and referenced documents. Here's a simple example:

```markdown
# Framework Context Definition

This file defines the documents and context to be loaded by the Dynamic Context Manager.

## System Documents

These documents define core personas and behavior.

- Catalyst Persona: @/path/to/catalyst_persona.md
- Forge Persona: @/path/to/forge_persona.md
- The AI-Assisted Dev Bible: @/path/to/ai_assisted_dev_bible.md
- MAIA-Workflow Framework: @/path/to/maia_workflow.md

## Project Documents

These documents are specific to this project.

- Project Requirements: @/path/to/requirements.md

## Initial Prompt

The following prompt will be sent as a system message at the start of the session.

```prompt
You are running in the AI-Assisted Framework with Catalyst and Forge personas.
Your task is to help the user with their website project. Start by introducing
yourself as Catalyst and offer to guide the user through the MAIA-Workflow process.
```
```

### Environment Variables

The framework supports several environment variables:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | API key for Google's Gemini models |
| `ANTHROPIC_API_KEY` | API key for Anthropic's Claude models |
| `FRAMEWORK_LOG_LEVEL` | Override for the framework log level |
| `PROJECT_DIR` | Path to the project directory (used in configuration values) |

## Using MAIA-Workflows

MAIA-Workflows (Multi-Step AI-Assisted Workflows) provide a structured approach to complex tasks. The workflow consists of a series of steps, each with defined inputs, actions, and outputs.

### Starting a MAIA-Workflow

You can start a MAIA-Workflow by asking Catalyst to initiate one:

```
> I'd like to start a MAIA-Workflow to create a simple web application.

(Catalyst): I'd be happy to guide you through a MAIA-Workflow for creating a simple web application. Let's set this up step by step.

MAIA-Workflow: "Simple Web Application Development"

Overall Goal: To design and implement a functional web application based on your requirements.

Let's start with Step 1: Requirements Gathering & Analysis.

In this step, I'll ask you some key questions to understand what you want to build. Could you please:
1. Describe the purpose of the web application
2. Identify your target users
3. List the main features you want to include
4. Mention any technology preferences or constraints

Once we have these details, we can move to the next steps of design, planning, and implementation.
```

### Following a MAIA-Workflow

Once a MAIA-Workflow is started, Catalyst will guide you through each step:

1. **Step Introduction**: Catalyst explains the current step and its goals
2. **User Input**: You provide the necessary information or decisions
3. **AI Processing**: The AI processes your input and generates outputs
4. **Step Completion**: Catalyst summarizes the outputs and transitions to the next step
5. **Workflow Completion**: When all steps are complete, Catalyst provides a final summary

### Workflow States

The framework saves the state of active MAIA-Workflows in the `maia_project_state.json` file. This allows you to resume workflows across multiple sessions.

## Advanced Usage

### Using Custom LLM Providers

To use a custom or new LLM provider:

1. **Update config.yaml** with your provider details:
   ```yaml
   llm:
     provider: "custom_provider"
     custom_provider:
       api_key: "${CUSTOM_API_KEY}"
       model: "custom-model"
       # Other provider-specific settings
   ```

2. **Implement a Custom Adapter** (requires development expertise, see Developer Guide)

### Managing Conversation Context

The framework intelligently manages conversation context to maintain coherent interactions with the LLM:

#### Prioritizing System Messages

By default, the framework prioritizes system messages during context pruning. This ensures that important instructions remain in the context.

#### Manual Context Management

You can manually manage the context:

- **Clear History**: Use `/clear` to reset the conversation (preserves system messages)
- **Add System Message**: Use `/system [message]` to add a new instruction
- **Targeted Questions**: Frame your questions to focus on specific aspects of the conversation

### Understanding the ICERC Protocol

ICERC (Intent, Command, Expected Outcome, Risk Assessment, Confirmation) is a security protocol used for all tool executions:

1. **Intent**: Explains why the tool is being used
2. **Command**: Shows exactly what will be executed
3. **Expected Outcome**: Describes what should happen if successful
4. **Risk Assessment**: Evaluates potential risks and their scope
5. **Confirmation**: Asks for explicit permission to proceed

This ensures transparency and user control over all operations performed by the framework.

## Troubleshooting

### Common Issues

#### LLM Provider Errors

**Problem**: "Failed to initialize LLM adapter"  
**Solution**: Check your API key, network connection, and provider settings in `config.yaml`

#### File Not Found Errors

**Problem**: "Context definition file not found"  
**Solution**: Verify the path in `dcm.context_definition_path` in your `config.yaml`

#### Permission Errors

**Problem**: "Failed to execute tool: Permission denied"  
**Solution**: Check file system permissions for the operations being attempted

### Logging

The framework logs detailed information to `framework.log` (or the path specified in `config.yaml`). For more verbose logs, set `framework.log_level` to `"DEBUG"`.

### Resetting the Framework

If you encounter persistent issues, you can reset the framework:

1. Stop the application (Ctrl+C or `/quit`)
2. Delete `maia_project_state.json` if it exists
3. Restart the application

## FAQ

**Q: Can I use multiple LLM providers simultaneously?**  
A: Currently, the framework uses one provider at a time as specified in the `llm.provider` setting.

**Q: How do I switch between Catalyst and Forge personas?**  
A: The framework automatically manages persona switching based on the task at hand. Catalyst handles strategic planning, while Forge handles implementation tasks.

**Q: Can I customize the personas?**  
A: Yes, you can modify the persona definitions referenced in `FRAMEWORK_CONTEXT.md`.

**Q: Is my data sent to third parties?**  
A: The framework only sends data to the configured LLM provider (e.g., Google for Gemini, Anthropic for Claude) as needed for processing your requests.

**Q: How do I update the framework?**  
A: Pull the latest changes from the repository and check for any migration steps in the release notes.

**Q: Can I run the framework offline?**  
A: The framework requires internet access to communicate with LLM providers. A fully offline version is not currently available.

**Q: How do I back up my work?**  
A: The framework saves state in `maia_project_state.json` and creates files in your project directory. Use standard backup methods, including Git if applicable.

---

This guide covers the basics of using the AI-Assisted Framework. For more detailed information on extending or customizing the framework, please refer to the Developer Guide.