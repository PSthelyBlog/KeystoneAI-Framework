# Framework Core API Reference

**Version:** 1.0.0-beta
**Date:** May 14, 2025

## Table of Contents
1. [Introduction](#introduction)
2. [Core Components Overview](#core-components-overview)
3. [Framework Controller](#framework-controller)
4. [Message Manager](#message-manager)
5. [UI Manager](#ui-manager)
6. [Tool Request Handler](#tool-request-handler)
7. [Error Handler](#error-handler)
8. [Component Managers](#component-managers)
   - [DCM Manager](#dcm-manager)
   - [LIAL Manager](#lial-manager)
   - [TEPS Manager](#teps-manager)
9. [Configuration](#configuration)
10. [Core Interfaces](#core-interfaces)
11. [Data Structures](#data-structures)
12. [Exceptions](#exceptions)

## Introduction

This document provides a comprehensive API reference for the Framework Core Application (V2). The framework is designed with a modular architecture centered around the LACA (LLM Agnostic Core Architecture) which features three primary components:

- **LIAL**: LLM Interaction Abstraction Layer
- **TEPS**: Tool Execution & Permission Service
- **DCM**: Dynamic Context Manager

These components are orchestrated by the Framework Controller, which manages the application lifecycle and user interaction flow.

## Core Components Overview

| Component | Description | Primary File |
|-----------|-------------|--------------|
| Framework Controller | Central orchestrator that initializes and manages all components | `controller.py` |
| Message Manager | Manages conversation history with pruning capabilities | `message_manager.py` |
| UI Manager | Handles user interface interaction | `ui_manager.py` |
| Tool Request Handler | Processes tool requests between LIAL and TEPS | `tool_request_handler.py` |
| Error Handler | Centralized error handling and reporting | `error_handler.py` |
| Configuration Loader | Loads and validates framework configuration | `config_loader.py` |
| DCM (Dynamic Context Manager) | Manages context definition files and document loading | `dcm.py` |
| LIAL (LLM Interaction Abstraction Layer) | Handles communication with LLMs via adapters | `lial_core.py` |
| TEPS (Tool Execution & Permission Service) | Manages tool execution with permission handling | `teps.py` |

## Framework Controller

**File:** `controller.py`  
**Class:** `FrameworkController`

The central orchestrator of the Framework Core Application. Manages component initialization, interaction flow, and lifecycle.

### Constructor

```python
def __init__(self, config_manager: 'ConfigurationManager')
```

**Parameters:**
- `config_manager`: Configuration manager instance that provides access to framework settings

### Methods

#### initialize()

```python
def initialize(self) -> bool
```

Initialize all framework components.

**Returns:** `bool` - True if initialization succeeded, False otherwise

#### run()

```python
def run(self) -> None
```

Run the main interaction loop. This is the primary entry point for the framework's operation after initialization.

**Raises:**
- `ComponentInitError`: If required components are not initialized

#### shutdown()

```python
def shutdown(self) -> None
```

Perform graceful shutdown of the framework.

### Protected Methods

#### _initialize_dcm()

```python
def _initialize_dcm(self) -> bool
```

Initialize the DCM component.

**Returns:** `bool` - True if initialization succeeded, False otherwise

#### _initialize_lial()

```python
def _initialize_lial(self) -> bool
```

Initialize the LIAL component with the appropriate adapter.

**Returns:** `bool` - True if initialization succeeded, False otherwise

#### _initialize_teps()

```python
def _initialize_teps(self) -> bool
```

Initialize the TEPS component.

**Returns:** `bool` - True if initialization succeeded, False otherwise

#### _setup_initial_context()

```python
def _setup_initial_context(self) -> None
```

Set up the initial context and prompt.

#### _process_messages_with_llm()

```python
def _process_messages_with_llm(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]
```

Process messages with the LLM via LIAL.

**Parameters:**
- `messages`: List of messages to send to the LLM

**Returns:** `Dict[str, Any]` - LLMResponse containing conversation and optional tool request

#### _handle_tool_request()

```python
def _handle_tool_request(self, tool_request: Dict[str, Any]) -> None
```

Handle a tool request via the Tool Request Handler.

**Parameters:**
- `tool_request`: The tool request to process

#### _process_special_command()

```python
def _process_special_command(self, user_input: str) -> bool
```

Process special commands starting with "/".

**Parameters:**
- `user_input`: The user input string

**Returns:** `bool` - True if a special command was processed, False otherwise

### Special Commands

The Framework Controller supports the following special commands:

| Command | Description |
|---------|-------------|
| `/help` | Show help message |
| `/quit` or `/exit` | Exit the application |
| `/clear` | Clear conversation history |
| `/system` | Add a system message |
| `/debug` | Toggle debug mode |

## Message Manager

**File:** `message_manager.py`  
**Class:** `MessageManager`

Manages conversation history and provides message pruning capabilities.

### Constructor

```python
def __init__(self, config: Optional[Dict[str, Any]] = None)
```

**Parameters:**
- `config`: Optional configuration dictionary with the following keys:
  - `max_length`: Maximum number of messages in history (default: 100)
  - `pruning_strategy`: Strategy for pruning history (default: "remove_oldest")
  - `prioritize_system_messages`: Whether to prioritize system messages (default: True)

### Methods

#### add_system_message()

```python
def add_system_message(self, content: str) -> None
```

Add a system message to the conversation history.

**Parameters:**
- `content`: The message content

#### add_user_message()

```python
def add_user_message(self, content: str) -> None
```

Add a user message to the conversation history.

**Parameters:**
- `content`: The message content

#### add_assistant_message()

```python
def add_assistant_message(self, content: str) -> None
```

Add an assistant message to the conversation history.

**Parameters:**
- `content`: The message content

#### add_tool_result_message()

```python
def add_tool_result_message(self, tool_name: str, content: Any, tool_call_id: str) -> None
```

Add a tool result message to the conversation history.

**Parameters:**
- `tool_name`: The name of the tool
- `content`: The tool result content
- `tool_call_id`: The ID of the tool call

#### get_messages()

```python
def get_messages(self, include_roles: Optional[List[str]] = None, exclude_roles: Optional[List[str]] = None, for_llm: bool = False) -> List[Dict[str, Any]]
```

Get messages from the conversation history with optional filtering.

**Parameters:**
- `include_roles`: Optional list of roles to include
- `exclude_roles`: Optional list of roles to exclude
- `for_llm`: Whether to format messages for LLM consumption

**Returns:** `List[Dict[str, Any]]` - List of message dictionaries

#### prune_history()

```python
def prune_history(self, preserve_system: bool = True) -> None
```

Prune the message history to prevent context window overflow.

**Parameters:**
- `preserve_system`: Whether to preserve system messages

#### clear_history()

```python
def clear_history(self, preserve_system: bool = True) -> None
```

Clear the message history.

**Parameters:**
- `preserve_system`: Whether to preserve system messages

#### serialize()

```python
def serialize(self) -> Dict[str, Any]
```

Serialize the message history for storage.

**Returns:** `Dict[str, Any]` - Dictionary representation of the message history

#### deserialize()

```python
def deserialize(self, data: Dict[str, Any]) -> None
```

Deserialize stored message history.

**Parameters:**
- `data`: Dictionary representation of message history

### Message Format

The internal message format uses the following structure:

```python
{
    "role": str,           # "system", "user", "assistant", or "tool_result"
    "content": str,        # Message content
    "timestamp": float,    # UNIX timestamp
    "tool_name": str,      # Only for tool_result messages
    "tool_call_id": str    # Only for tool_result messages
}
```

When formatting for LLM consumption (`for_llm=True`), the format is:

```python
{
    "role": str,           # "system", "user", "assistant", or "tool"
    "content": str,        # Message content
    "name": str,           # Only for tool messages, contains tool_name
    "tool_call_id": str    # Only for tool messages
}
```

## UI Manager

**File:** `ui_manager.py`  
**Class:** `UserInterfaceManager`

Handles user interface interaction, including display formatting and input processing.

### Constructor

```python
def __init__(self, config: Optional[Dict[str, Any]] = None)
```

**Parameters:**
- `config`: Optional configuration dictionary controlling UI behavior

### Methods

#### get_user_input()

```python
def get_user_input(self) -> str
```

Get input from the user.

**Returns:** `str` - User input string

#### display_system_message()

```python
def display_system_message(self, message: str) -> None
```

Display a system message to the user.

**Parameters:**
- `message`: The message content to display

#### display_user_message()

```python
def display_user_message(self, message: str) -> None
```

Display a user message (echo).

**Parameters:**
- `message`: The message content to display

#### display_assistant_message()

```python
def display_assistant_message(self, message: str) -> None
```

Display an assistant message to the user.

**Parameters:**
- `message`: The message content to display

#### display_error_message()

```python
def display_error_message(self, error_type: str, error_message: str) -> None
```

Display an error message to the user.

**Parameters:**
- `error_type`: The type of error
- `error_message`: The error message content

#### display_special_command_help()

```python
def display_special_command_help(self, commands: Dict[str, str]) -> None
```

Display help for special commands.

**Parameters:**
- `commands`: Dictionary mapping commands to their descriptions

## Tool Request Handler

**File:** `tool_request_handler.py`  
**Class:** `ToolRequestHandler`

Processes tool requests between LIAL and TEPS, handling formatting and execution.

### Constructor

```python
def __init__(self, teps_manager: 'TEPSManager')
```

**Parameters:**
- `teps_manager`: TEPS Manager instance

### Methods

#### process_tool_request()

```python
def process_tool_request(self, tool_request: Dict[str, Any]) -> Dict[str, Any]
```

Process a tool request via TEPS.

**Parameters:**
- `tool_request`: The tool request to process

**Returns:** `Dict[str, Any]` - Tool execution result

**Raises:**
- `ToolExecutionError`: If tool execution fails

#### format_tool_result_as_message()

```python
def format_tool_result_as_message(self, tool_result: Dict[str, Any]) -> Dict[str, Any]
```

Format a tool result as a message for the conversation history.

**Parameters:**
- `tool_result`: The tool result to format

**Returns:** `Dict[str, Any]` - Formatted tool result message

## Error Handler

**File:** `error_handler.py`  
**Class:** `ErrorHandler`

Centralizes error handling and reporting across the framework.

### Constructor

```python
def __init__(self)
```

### Methods

#### handle_error()

```python
def handle_error(self, error_type: str, error_message: str, exception: Optional[Exception] = None) -> str
```

Handle an error and generate a user-friendly error message.

**Parameters:**
- `error_type`: Type of error (e.g., "Initialization Error")
- `error_message`: The error message
- `exception`: Optional exception object

**Returns:** `str` - User-friendly error message

#### log_error()

```python
def log_error(self, error_type: str, error_message: str, exception: Optional[Exception] = None) -> None
```

Log an error to the framework logs.

**Parameters:**
- `error_type`: Type of error
- `error_message`: The error message
- `exception`: Optional exception object

## Component Managers

### DCM Manager

**File:** `component_managers/dcm_manager.py`  
**Class:** `DCMManager`

Manages the Dynamic Context Manager (DCM) component.

### Constructor

```python
def __init__(self, context_definition_path: str)
```

**Parameters:**
- `context_definition_path`: Path to the FRAMEWORK_CONTEXT.md file

### Methods

#### initialize()

```python
def initialize(self) -> None
```

Initialize the DCM component.

**Raises:**
- `DCMInitError`: If initialization fails

#### get_initial_prompt()

```python
def get_initial_prompt(self) -> Optional[str]
```

Get the initial prompt from the context definition.

**Returns:** `Optional[str]` - Initial prompt string or None if not defined

#### get_document_content()

```python
def get_document_content(self, document_id: str) -> Optional[str]
```

Get the content of a document by its ID.

**Parameters:**
- `document_id`: The ID of the document

**Returns:** `Optional[str]` - Document content or None if not found

#### get_context_section()

```python
def get_context_section(self, section_id: str) -> Optional[str]
```

Get a section of the context by its ID.

**Parameters:**
- `section_id`: The ID of the section

**Returns:** `Optional[str]` - Section content or None if not found

### LIAL Manager

**File:** `component_managers/lial_manager.py`  
**Class:** `LIALManager`

Manages the LLM Interaction Abstraction Layer.

### Constructor

```python
def __init__(self, llm_provider: str, llm_settings: Dict[str, Any], dcm_manager: Optional['DCMManager'] = None)
```

**Parameters:**
- `llm_provider`: The LLM provider name (e.g., "gemini")
- `llm_settings`: Settings for the LLM provider
- `dcm_manager`: Optional DCM Manager instance for context integration

### Methods

#### initialize()

```python
def initialize(self) -> None
```

Initialize the LIAL component with the appropriate adapter.

**Raises:**
- `LIALInitError`: If initialization fails

#### send_messages()

```python
def send_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]
```

Send messages to the LLM and get a response.

**Parameters:**
- `messages`: List of messages to send to the LLM

**Returns:** `Dict[str, Any]` - LLM response with conversation and optional tool request

**Raises:**
- `LIALError`: If sending messages fails

### TEPS Manager

**File:** `component_managers/teps_manager.py`  
**Class:** `TEPSManager`

Manages the Tool Execution & Permission Service.

### Constructor

```python
def __init__(self, teps_settings: Dict[str, Any])
```

**Parameters:**
- `teps_settings`: Settings for the TEPS component

### Methods

#### initialize()

```python
def initialize(self) -> None
```

Initialize the TEPS component.

**Raises:**
- `TEPSInitError`: If initialization fails

#### execute_tool()

```python
def execute_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]
```

Execute a tool based on the provided request.

**Parameters:**
- `tool_request`: Tool request with name, parameters, etc.

**Returns:** `Dict[str, Any]` - Tool execution result

**Raises:**
- `ToolExecutionError`: If tool execution fails

#### request_permission()

```python
def request_permission(self, icerc_data: Dict[str, Any]) -> bool
```

Request permission from the user for tool execution using the ICERC protocol.

**Parameters:**
- `icerc_data`: ICERC data with intent, command, etc.

**Returns:** `bool` - True if permission granted, False otherwise

## Configuration

**File:** `config_loader.py`  
**Class:** `ConfigurationManager`

Loads and validates framework configuration.

### Constructor

```python
def __init__(self, config_path: str = None)
```

**Parameters:**
- `config_path`: Optional path to the configuration file

### Methods

#### load_config()

```python
def load_config(self, config_path: str) -> Dict[str, Any]
```

Load configuration from file.

**Parameters:**
- `config_path`: Path to the configuration file

**Returns:** `Dict[str, Any]` - Loaded configuration

**Raises:**
- `ConfigError`: If loading or validating fails

#### get_llm_provider()

```python
def get_llm_provider(self) -> str
```

Get the configured LLM provider.

**Returns:** `str` - LLM provider name

#### get_llm_settings()

```python
def get_llm_settings(self) -> Dict[str, Any]
```

Get the settings for the configured LLM provider.

**Returns:** `Dict[str, Any]` - LLM settings

#### get_context_definition_path()

```python
def get_context_definition_path(self) -> str
```

Get the path to the context definition file.

**Returns:** `str` - Path to FRAMEWORK_CONTEXT.md

#### get_teps_settings()

```python
def get_teps_settings(self) -> Dict[str, Any]
```

Get the settings for the TEPS component.

**Returns:** `Dict[str, Any]` - TEPS settings

#### get_message_history_settings()

```python
def get_message_history_settings(self) -> Dict[str, Any]
```

Get the settings for message history management.

**Returns:** `Dict[str, Any]` - Message history settings

#### get_ui_settings()

```python
def get_ui_settings(self) -> Dict[str, Any]
```

Get the settings for the UI manager.

**Returns:** `Dict[str, Any]` - UI settings

## Core Interfaces

### LLMAdapterInterface

**File:** `lial_core.py`  
**Class:** `LLMAdapterInterface`

Interface for LLM Adapters to implement.

### Methods

#### send_messages()

```python
def send_messages(self, messages: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
```

Send messages to the LLM and get a response.

**Parameters:**
- `messages`: List of messages to send to the LLM
- `options`: Optional provider-specific options

**Returns:** `Dict[str, Any]` - LLM response with conversation and optional tool request

### ToolHandlerInterface

**File:** `teps.py`  
**Class:** `ToolHandlerInterface`

Interface for Tool Handlers to implement.

### Methods

#### execute()

```python
def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]
```

Execute the tool with the given parameters.

**Parameters:**
- `parameters`: Tool parameters

**Returns:** `Dict[str, Any]` - Tool execution result

## Data Structures

### Message

Standard message format in memory:

```python
{
    "role": str,           # "system", "user", "assistant", or "tool_result"
    "content": str,        # Message content
    "timestamp": float,    # UNIX timestamp
    "tool_name": str,      # Only for tool_result messages
    "tool_call_id": str    # Only for tool_result messages
}
```

### LLMResponse

```python
{
    "conversation": str,                  # Text response from the LLM
    "tool_request": Optional[Dict[str, Any]]  # Optional tool request (if LLM requested a tool)
}
```

### ToolRequest

```python
{
    "request_id": str,        # Unique ID for this request
    "tool_name": str,         # Name of the tool to execute
    "parameters": Dict[str, Any],  # Parameters for the tool
    "icerc": Dict[str, Any]   # ICERC data for permission
}
```

### ToolResult

```python
{
    "request_id": str,     # ID from the original request
    "tool_name": str,      # Name of the tool that was executed
    "success": bool,       # Whether execution was successful
    "content": Any,        # Result content
    "error": Optional[str] # Error message if success is False
}
```

### ICERC

ICERC (Intent, Command, Expected Outcome, Risk Assessment, Confirmation) format:

```python
{
    "intent": str,           # The intent behind the command
    "command": str,          # The actual command to execute
    "expected_outcome": str, # What should happen if successful
    "risk_assessment": {
        "level": str,        # "low", "medium", "high"
        "scope": str,        # Scope of impact
        "details": str       # Additional risk details
    }
}
```

## Exceptions

All Framework-specific exceptions are defined in `exceptions/__init__.py`.

### Base Exceptions

#### FrameworkError

Base exception for all framework errors.

#### ConfigError

Error related to configuration loading or validation.

#### ComponentInitError

Error initializing a framework component.

### Component-Specific Exceptions

#### DCMInitError

Error initializing the DCM component.

#### LIALInitError

Error initializing the LIAL component.

#### LIALError

Error in LIAL operation.

#### TEPSInitError

Error initializing the TEPS component.

#### ToolExecutionError

Error executing a tool.

---

## Usage Examples

### Initialize and Run the Framework

```python
from framework_core.config_loader import ConfigurationManager
from framework_core.controller import FrameworkController

# Initialize configuration
config_manager = ConfigurationManager('/path/to/config.yaml')

# Initialize controller
controller = FrameworkController(config_manager)

# Initialize all components
if controller.initialize():
    # Start the main loop
    controller.run()
else:
    print("Framework initialization failed")
```

### Custom Message History Management

```python
from framework_core.message_manager import MessageManager

# Initialize with custom settings
message_manager = MessageManager({
    "max_length": 50,
    "pruning_strategy": "remove_oldest",
    "prioritize_system_messages": True
})

# Add messages
message_manager.add_system_message("You are a helpful assistant.")
message_manager.add_user_message("Hello, can you help me?")
message_manager.add_assistant_message("Yes, I can help you with your questions.")

# Get messages for LLM
messages = message_manager.get_messages(for_llm=True)

# Prune history
message_manager.prune_history(preserve_system=True)
```

### Tool Execution Through TEPS

```python
from framework_core.component_managers.teps_manager import TEPSManager

# Initialize TEPS
teps_manager = TEPSManager({
    "permission_required": True,
    "allowed_tools": ["file_read", "web_search"]
})
teps_manager.initialize()

# Execute tool
tool_result = teps_manager.execute_tool({
    "request_id": "req123",
    "tool_name": "file_read",
    "parameters": {"file_path": "/path/to/file.txt"},
    "icerc": {
        "intent": "Read file content",
        "command": "Read '/path/to/file.txt'",
        "expected_outcome": "File content retrieved",
        "risk_assessment": {
            "level": "low",
            "scope": "File system read-only operation",
            "details": "No modification will occur"
        }
    }
})
```