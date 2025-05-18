# AI-Assisted Framework Developer Guide (v2.0.0)

**Date:** May 14, 2025

## Table of Contents
1. [Introduction](#introduction)
2. [Architectural Overview](#architectural-overview)
    - [Framework Core Application](#framework-core-application)
    - [LIAL (LLM Interaction Abstraction Layer)](#lial-llm-interaction-abstraction-layer)
    - [TEPS (Tool Execution & Permission Service)](#teps-tool-execution--permission-service)
    - [DCM (Dynamic Context Manager)](#dcm-dynamic-context-manager)
    - [System Flow and Component Interactions](#system-flow-and-component-interactions)
3. [Configuration](#configuration)
    - [config.yaml Options](#configyaml-options)
    - [FRAMEWORK_CONTEXT.md Syntax](#framework_contextmd-syntax)
    - [Environment Variables](#environment-variables)
4. [LIAL Development](#lial-development)
    - [LLMAdapterInterface Specification](#llmadapterinterface-specification)
    - [Creating New LIAL Adapters](#creating-new-lial-adapters)
    - [Message Formatting and Error Handling](#message-formatting-and-error-handling)
5. [TEPS Development](#teps-development)
    - [ToolRequest and ToolResult Structures](#toolrequest-and-toolresult-structures)
    - [Adding New Tools](#adding-new-tools)
    - [ICERC Protocol Implementation](#icerc-protocol-implementation)
    - [Security Considerations](#security-considerations)
6. [DCM Usage & Extension](#dcm-usage--extension)
    - [Context Definition File Format](#context-definition-file-format)
    - [Document Loading and Management](#document-loading-and-management)
    - [Integration with LIAL](#integration-with-lial)
7. [Framework Core Extension](#framework-core-extension)
    - [MessageManager Customization](#messagemanager-customization)
    - [UI Extension Patterns](#ui-extension-patterns)
    - [Error Handling Strategies](#error-handling-strategies)
8. [Logging and Debugging](#logging-and-debugging)
    - [Log Format and Levels](#log-format-and-levels)
    - [Debugging Techniques](#debugging-techniques)
    - [Common Errors and Solutions](#common-errors-and-solutions)
9. [Testing](#testing)
    - [Framework Testing Approach](#framework-testing-approach)
    - [Writing Unit Tests](#writing-unit-tests)
    - [Writing Integration Tests](#writing-integration-tests)
    - [Mocking Strategies](#mocking-strategies)
10. [Contribution Guidelines](#contribution-guidelines)
    - [Coding Standards](#coding-standards)
    - [Pull Request Process](#pull-request-process)
    - [Documentation Requirements](#documentation-requirements)

## Introduction

The AI-Assisted Framework Version 2.0.0 is designed with a modular, extensible architecture that supports LLM-agnostic operation. This guide provides detailed technical information for developers who want to understand, extend, or contribute to the framework.

This version introduces the LACA (LLM Agnostic Core Architecture) which decouples the framework from specific LLM providers and provides clear extension points for customization.

### Key Improvements in Version 2.0.0

- **LLM Provider Independence**: No longer tied to Claude Code API specifically
- **Modular Component Architecture**: Clearly separated components with well-defined interfaces
- **Enhanced Security**: Standardized ICERC permission protocol for all system operations
- **Robust Error Handling**: Comprehensive error handling throughout the framework
- **Comprehensive Testing**: Extensive unit and integration tests
- **Improved Documentation**: Complete API reference and developer guides

## Architectural Overview

The framework is structured around four major components:

1. **Framework Core Application**: Central orchestrator and integration layer
2. **LIAL (LLM Interaction Abstraction Layer)**: Handles communication with LLMs
3. **TEPS (Tool Execution & Permission Service)**: Manages tool execution with permission handling
4. **DCM (Dynamic Context Manager)**: Manages context documents and framework initialization

### Framework Core Application

The Framework Core Application serves as the central orchestrator and integration layer. It is responsible for:

- Initializing all components
- Managing the interaction flow
- Processing user input and displaying responses
- Routing tool requests and results
- Handling errors and shutdown

Key classes in the Framework Core Application include:

- `FrameworkController`: Central orchestrator that initializes and manages components
- `MessageManager`: Manages conversation history with pruning capabilities
- `UserInterfaceManager`: Handles user interface interaction
- `ToolRequestHandler`: Processes tool requests between LIAL and TEPS
- `ErrorHandler`: Centralizes error handling and reporting
- `ConfigurationManager`: Loads and validates configuration

### LIAL (LLM Interaction Abstraction Layer)

LIAL abstracts communication with LLMs behind a provider-agnostic interface. It is responsible for:

- Sending messages to the LLM
- Processing LLM responses
- Extracting tool requests from LLM responses
- Formatting messages for specific LLM providers
- Error handling and retries

Key components of LIAL include:

- `LIALManager`: Manages the LIAL component and selects the appropriate adapter
- `LLMAdapterInterface`: Interface that all LLM adapters must implement
- Specific adapters (e.g., `GeminiAdapter`): Implements provider-specific communication

### TEPS (Tool Execution & Permission Service)

TEPS manages the execution of tools with appropriate permissions and security checks. It is responsible for:

- Processing tool requests
- Implementing the ICERC permission protocol
- Executing tools safely
- Handling tool execution errors
- Returning tool results

Key components of TEPS include:

- `TEPSManager`: Manages the TEPS component
- `ToolHandlerInterface`: Interface that all tool handlers must implement
- Specific tool handlers (e.g., `FileSystemHandler`, `WebSearchHandler`)

### DCM (Dynamic Context Manager)

DCM manages context documents and provides them to other components. It is responsible for:

- Loading and parsing the framework context definition file (FRAMEWORK_CONTEXT.md)
- Loading referenced documents
- Providing access to sections of context documents
- Managing the initial prompt

Key components of DCM include:

- `DCMManager`: Manages the DCM component
- `ContextParser`: Parses context definition files
- `DocumentLoader`: Loads and validates documents

### System Flow and Component Interactions

The following diagram illustrates the flow of data through the framework's components:

```
                   ┌─────────────────┐
                   │                 │
                   │      User       │
                   │                 │
                   └─────────┬───────┘
                             │
                             ▼
┌───────────────────────────────────────────────────┐
│                                                   │
│               Framework Controller                │
│                                                   │
└───┬─────────────────┬───────────────────────┬────┘
    │                 │                       │
    ▼                 ▼                       ▼
┌─────────┐    ┌─────────────┐        ┌─────────────┐
│         │    │             │        │             │
│   UI    │    │   Message   │        │    Tool     │
│ Manager │    │   Manager   │        │   Request   │
│         │    │             │        │   Handler   │
└────┬────┘    └──────┬──────┘        └──────┬──────┘
     │               │                       │
     │               │                       │
     │               ▼                       │
     │         ┌─────────────┐               │
     │         │             │               │
     │         │    LIAL     │◀──────────────┘
     │         │   Manager   │    Tool Results
     │         │             │
     │         └──────┬──────┘
     │                │
     │                ▼
     │         ┌─────────────┐         ┌─────────────┐
     │         │             │         │             │
     │         │    LLM      │         │    DCM      │
     │         │   Adapter   │         │   Manager   │
     │         │             │         │             │
     │         └──────┬──────┘         └──────┬──────┘
     │                │                        │
     │                ▼                        │
     │         ┌─────────────┐                 │
     │         │             │                 │
     │         │    LLM      │                 │
     │         │   Provider  │                 │
     │         │             │                 │
     │         └──────┬──────┘                 │
     │                │                        │
     │                │                        │
     ▼                ▼                        ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
│                      User                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Typical Flow:**

1. User provides input through the UI Manager
2. Framework Controller adds the message to Message Manager
3. Controller gets messages from Message Manager and passes them to LIAL
4. LIAL formats messages for the specific LLM adapter and sends to LLM provider
5. LLM responds with text and optional tool requests
6. If a tool request is present, it's routed to the Tool Request Handler
7. Tool Request Handler passes the request to TEPS
8. TEPS presents ICERC to the user and waits for permission
9. If permission is granted, TEPS executes the tool and returns results
10. Tool results are added to the message history
11. Cycle repeats

## Configuration

The framework is configured through a YAML file (`config.yaml`) and a context definition file (`FRAMEWORK_CONTEXT.md`).

### config.yaml Options

The `config.yaml` file controls the behavior of the framework and its components. Here's a comprehensive list of configuration options:

#### General Settings

```yaml
# General framework settings
framework:
  name: "AI-Assisted Framework"
  version: "2.0.0"
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_file: "framework.log"
```

#### LLM Provider Settings

```yaml
# LLM provider configuration
llm:
  provider: "gemini"  # Currently supported: gemini, anthropic (planned)
  gemini:
    api_key: "${GEMINI_API_KEY}"  # Environment variable reference
    model: "gemini-1.5-pro"
    temperature: 0.7
    max_output_tokens: 8192
    top_p: 0.95
    top_k: 40
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-opus-20240229"
    temperature: 0.7
    max_tokens: 4096
```

#### TEPS Settings

```yaml
# Tool Execution & Permission Service configuration
teps:
  permission_required: true
  allowed_tools:
    - "file_read"
    - "file_write"
    - "web_search"
    - "bash"
  secure_mode: true
  tool_timeout: 30000  # milliseconds
  bash:
    allowed_commands:
      - "ls"
      - "cat"
      - "echo"
    blocked_commands:
      - "rm"
      - "sudo"
    working_directory: "${PROJECT_DIR}"
```

#### Message History Settings

```yaml
# Message Manager configuration
message_history:
  max_length: 100
  pruning_strategy: "remove_oldest"  # remove_oldest, summarize (planned)
  prioritize_system_messages: true
```

#### UI Settings

```yaml
# UI Manager configuration
ui:
  color_enabled: true
  debug_mode: false
  show_timestamps: false
  prompt_symbol: ">"
```

#### DCM Settings

```yaml
# Dynamic Context Manager configuration
dcm:
  context_definition_path: "${PROJECT_DIR}/FRAMEWORK_CONTEXT.md"
  max_document_size: 10485760  # 10MB
  document_cache_enabled: true
  document_cache_size: 20
```

### FRAMEWORK_CONTEXT.md Syntax

The `FRAMEWORK_CONTEXT.md` file defines the context for the framework, including system prompts and referenced documents. Here's the standard syntax:

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
- Architecture Design: @/path/to/architecture.md

## Initial Prompt

The following prompt will be sent as a system message at the start of the session.

```prompt
You are running in the AI-Assisted Framework with Catalyst and Forge personas.
Your task is to help the user with their projects using the MAIA-Workflow methodology.
```
```

#### Syntax Rules

- **Document References**: Use `@` followed by the path to reference a document
- **Sections**: Use `##` to create sections that can be accessed independently
- **Initial Prompt**: The `## Initial Prompt` section is special and will be used as the first system message
- **Code Blocks**: Use triple backticks with a language identifier (e.g., ```prompt) for formatted blocks

### Environment Variables

The framework supports environment variable substitution in configuration values. Here are the commonly used environment variables:

- `PROJECT_DIR`: The directory containing the project
- `GEMINI_API_KEY`: API key for Google's Gemini models
- `ANTHROPIC_API_KEY`: API key for Anthropic's Claude models
- `FRAMEWORK_LOG_LEVEL`: Override for the framework log level

Environment variables are referenced with `${VAR_NAME}` syntax in the configuration files.

## LIAL Development

The LLM Interaction Abstraction Layer (LIAL) is designed to be extensible with new LLM providers. This section covers the details of the `LLMAdapterInterface` and how to implement new adapters.

### LLMAdapterInterface Specification

All LLM adapters must implement the `LLMAdapterInterface` defined in `lial_core.py`. Here's the full interface definition:

```python
class LLMAdapterInterface:
    """Interface for LLM Adapters to implement."""
    
    def initialize(self, settings: Dict[str, Any]) -> None:
        """
        Initialize the adapter with provider-specific settings.
        
        Args:
            settings: Provider-specific settings
            
        Raises:
            LIALError: If initialization fails
        """
        raise NotImplementedError("Subclasses must implement initialize()")
    
    def send_messages(
        self, 
        messages: List[Dict[str, Any]], 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send messages to the LLM and get a response.
        
        Args:
            messages: List of messages to send to the LLM
            options: Optional provider-specific options
            
        Returns:
            Dict containing:
                - conversation: Text response from the LLM
                - tool_request: Optional tool request if the LLM requested a tool
                
        Raises:
            LIALError: If sending messages fails
        """
        raise NotImplementedError("Subclasses must implement send_messages()")
        
    def supports_tool_use(self) -> bool:
        """
        Whether this adapter supports tool use.
        
        Returns:
            True if tool use is supported, False otherwise
        """
        raise NotImplementedError("Subclasses must implement supports_tool_use()")
        
    def get_provider_name(self) -> str:
        """
        Get the name of the LLM provider.
        
        Returns:
            Provider name string
        """
        raise NotImplementedError("Subclasses must implement get_provider_name()")
```

### Creating New LIAL Adapters

Here's a step-by-step guide to creating a new LIAL adapter:

1. **Create a new file** in the `framework_core/adapters/` directory (e.g., `custom_adapter.py`)

2. **Import the interface**:
   ```python
   from typing import Dict, List, Any, Optional
   from framework_core.lial_core import LLMAdapterInterface
   from framework_core.exceptions import LIALError
   ```

3. **Implement the adapter class**:
   ```python
   class CustomAdapter(LLMAdapterInterface):
       """Adapter for Custom LLM provider."""
       
       def __init__(self):
           self.initialized = False
           self.api_key = None
           self.model = None
           self.client = None
           
       def initialize(self, settings: Dict[str, Any]) -> None:
           """Initialize the adapter with settings."""
           try:
               self.api_key = settings.get("api_key")
               if not self.api_key:
                   raise LIALError("API key not provided for Custom adapter")
                   
               self.model = settings.get("model", "default-model")
               
               # Initialize client library or API client
               self.client = CustomClient(api_key=self.api_key)
               
               self.initialized = True
           except Exception as e:
               raise LIALError(f"Failed to initialize Custom adapter: {str(e)}")
               
       def send_messages(
           self, 
           messages: List[Dict[str, Any]], 
           options: Optional[Dict[str, Any]] = None
       ) -> Dict[str, Any]:
           """Send messages to the LLM and get a response."""
           if not self.initialized:
               raise LIALError("Custom adapter not initialized")
               
           try:
               # Convert messages to provider-specific format
               provider_messages = self._convert_messages(messages)
               
               # Set up request options
               request_options = {
                   "model": self.model,
                   "temperature": options.get("temperature", 0.7) if options else 0.7,
                   # Add other options
               }
               
               # Send request to provider
               response = self.client.generate(provider_messages, **request_options)
               
               # Process and extract the response
               result = {
                   "conversation": self._extract_text(response),
                   "tool_request": self._extract_tool_request(response)
               }
               
               return result
               
           except Exception as e:
               raise LIALError(f"Error sending messages to Custom LLM: {str(e)}")
       
       def supports_tool_use(self) -> bool:
           """Whether this adapter supports tool use."""
           return True  # Set to True or False based on provider capabilities
           
       def get_provider_name(self) -> str:
           """Get the name of the LLM provider."""
           return "custom"
           
       # Helper methods
       def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
           """Convert framework message format to provider-specific format."""
           # Implement conversion logic
           return provider_messages
           
       def _extract_text(self, response: Any) -> str:
           """Extract text response from provider response."""
           # Implement extraction logic
           return text
           
       def _extract_tool_request(self, response: Any) -> Optional[Dict[str, Any]]:
           """Extract tool request from provider response if present."""
           # Implement extraction logic
           return tool_request if has_tool_request else None
   ```

4. **Register the adapter** in `lial_core.py`:
   ```python
   # In LIALManager._get_adapter method
   def _get_adapter(self, provider_name: str) -> LLMAdapterInterface:
       """Get the appropriate adapter for the provider."""
       if provider_name == "gemini":
           from framework_core.adapters.gemini_adapter import GeminiAdapter
           return GeminiAdapter()
       elif provider_name == "custom":  # Add your adapter here
           from framework_core.adapters.custom_adapter import CustomAdapter
           return CustomAdapter()
       else:
           raise LIALInitError(f"Unsupported provider: {provider_name}")
   ```

5. **Add settings** to `config.yaml`:
   ```yaml
   llm:
     provider: "custom"
     custom:
       api_key: "${CUSTOM_API_KEY}"
       model: "custom-model-name"
       # Other provider-specific settings
   ```

### Message Formatting and Error Handling

#### Standard Message Format

The framework uses a standardized message format that adapters must translate to and from the provider-specific format:

```python
# Standard framework message format
{
    "role": str,           # "system", "user", "assistant", or "tool"
    "content": str,        # Message content
    "name": str,           # Only for tool messages, contains tool_name
    "tool_call_id": str    # Only for tool messages
}
```

#### Tool Request Format

If an LLM requests a tool, the adapter should return it in this format:

```python
# Tool request format
{
    "request_id": str,       # Unique ID for this request
    "tool_name": str,        # Name of the tool to execute
    "parameters": Dict,      # Parameters for the tool
}
```

#### Error Handling Best Practices

1. **Initialization Errors**: Wrap provider-specific errors in `LIALError` with clear messages
2. **API Errors**: Handle connection issues, rate limits, and authorization errors
3. **Input Validation**: Validate messages before sending to the provider
4. **Output Validation**: Ensure the response matches the expected format
5. **Retries**: Implement retries for transient errors with exponential backoff

## TEPS Development

The Tool Execution & Permission Service (TEPS) provides a standardized interface for tool execution with permission handling. This section covers the `ToolRequest` and `ToolResult` data structures, how to add new tools, and security considerations.

### ToolRequest and ToolResult Structures

#### ToolRequest

```python
# Tool request structure
{
    "request_id": str,       # Unique ID for this request
    "tool_name": str,        # Name of the tool to execute
    "parameters": Dict,      # Parameters for the tool
    "icerc": {               # ICERC data for permission
        "intent": str,       # The intent behind the command
        "command": str,      # The actual command to execute
        "expected_outcome": str,  # What should happen if successful
        "risk_assessment": {
            "level": str,    # "low", "medium", "high"
            "scope": str,    # Scope of impact
            "details": str   # Additional risk details
        }
    }
}
```

#### ToolResult

```python
# Tool result structure
{
    "request_id": str,     # ID from the original request
    "tool_name": str,      # Name of the tool that was executed
    "success": bool,       # Whether execution was successful
    "content": Any,        # Result content
    "error": Optional[str] # Error message if success is False
}
```

### Adding New Tools

To add a new tool to TEPS, follow these steps:

1. **Create a Tool Handler class** that implements `ToolHandlerInterface`:

```python
from typing import Dict, Any, Optional
from framework_core.teps import ToolHandlerInterface
from framework_core.exceptions import ToolExecutionError

class CustomToolHandler(ToolHandlerInterface):
    """Handler for a custom tool."""
    
    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """Initialize the tool handler."""
        self.settings = settings or {}
        
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Tool execution result
            
        Raises:
            ToolExecutionError: If execution fails
        """
        try:
            # Validate parameters
            self._validate_parameters(parameters)
            
            # Execute the tool logic
            result = self._perform_action(parameters)
            
            # Return the result
            return result
            
        except Exception as e:
            raise ToolExecutionError(f"Error executing custom tool: {str(e)}")
            
    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate the parameters."""
        # Implement validation logic
        required_params = ["param1", "param2"]
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")
                
    def _perform_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the actual tool action."""
        # Implement tool logic
        result = {
            "output": "Result of the custom tool execution",
            "details": {"param1": parameters["param1"]}
        }
        return result
    
    def generate_icerc(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate ICERC data for permission request.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            ICERC data
        """
        return {
            "intent": f"Execute custom tool with {parameters['param1']}",
            "command": f"custom_tool({parameters['param1']}, {parameters['param2']})",
            "expected_outcome": "Perform the custom action and return results",
            "risk_assessment": {
                "level": "low",
                "scope": "Application-specific action",
                "details": "This tool only performs safe operations within the application"
            }
        }
```

2. **Register the Tool Handler** in `teps.py`:

```python
# In TEPSManager._initialize_tool_handlers method
def _initialize_tool_handlers(self) -> None:
    """Initialize the tool handlers."""
    self.tool_handlers = {
        "file_read": FileSystemHandler(self.settings.get("file_read", {})),
        "file_write": FileSystemHandler(self.settings.get("file_write", {})),
        "web_search": WebSearchHandler(self.settings.get("web_search", {})),
        "bash": BashHandler(self.settings.get("bash", {})),
        "custom_tool": CustomToolHandler(self.settings.get("custom_tool", {}))  # Add your tool here
    }
```

3. **Add Settings** to `config.yaml`:

```yaml
teps:
  allowed_tools:
    - "file_read"
    - "file_write"
    - "web_search"
    - "bash"
    - "custom_tool"  # Add your tool here
  custom_tool:       # Tool-specific settings
    setting1: "value1"
    setting2: "value2"
```

### ICERC Protocol Implementation

The ICERC (Intent, Command, Expected Outcome, Risk Assessment, Confirmation) protocol is a key security feature of TEPS. It ensures that users explicitly approve all tool operations that could have side effects.

#### ICERC Structure

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

#### Typical Flow

1. LLM requests a tool via LIAL
2. Tool Request Handler preprocesses the request and passes it to TEPS
3. TEPS generates ICERC data or uses provided ICERC data
4. TEPS displays ICERC to the user and requests permission
5. User reviews ICERC data and grants or denies permission
6. If permission is granted, TEPS executes the tool
7. Tool result is returned to Tool Request Handler

### Security Considerations

When implementing new tools or customizing existing ones, keep these security principles in mind:

1. **Principle of Least Privilege**: Tools should only have access to resources they absolutely need
2. **Input Validation**: Validate all parameters before execution
3. **Path Traversal Prevention**: For file operations, validate and sanitize paths
4. **Command Injection Prevention**: For bash operations, validate commands against an allowlist
5. **Rate Limiting**: Implement rate limiting for tools that access external resources
6. **Clear ICERC**: Ensure ICERC data clearly communicates the action and potential risks

## DCM Usage & Extension

The Dynamic Context Manager (DCM) manages context documents and provides them to other components. This section covers the context definition file format, document loading, and integration with LIAL.

### Context Definition File Format

The `FRAMEWORK_CONTEXT.md` file uses a specific format to define sections and reference documents:

```markdown
# Framework Context Definition

## Section 1

Content for section 1...

- Document 1: @/path/to/document1.md
- Document 2: @/path/to/document2.md

## Section 2

Content for section 2...

## Initial Prompt

```prompt
System prompt content...
```
```

#### Standard Sections

- `# Framework Context Definition`: The root heading
- `## Initial Prompt`: Contains the initial system prompt for the session
- `## Section X`: Custom sections that can be accessed by ID

#### Document References

Documents are referenced with `@` followed by the path. DCM will load these documents and make them available to other components.

### Document Loading and Management

DCM handles document loading, caching, and access:

```python
# Get the initial prompt
initial_prompt = dcm_manager.get_initial_prompt()

# Get a document by its ID
document_content = dcm_manager.get_document_content("document_id")

# Get a section by its ID
section_content = dcm_manager.get_context_section("section_id")
```

#### Supported Document Types

- Markdown (`.md`)
- Text (`.txt`)
- YAML (`.yaml`, `.yml`)
- JSON (`.json`)

#### Document Caching

DCM implements document caching to improve performance. The cache size can be configured in `config.yaml`:

```yaml
dcm:
  document_cache_enabled: true
  document_cache_size: 20
```

### Integration with LIAL

DCM integrates with LIAL to provide context for LLM interactions:

```python
# In LIALManager.send_messages
def send_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Send messages to the LLM and get a response."""
    # Enhance messages with DCM context if available
    if self.dcm_manager:
        messages = self._enhance_with_context(messages)
        
    # Send to adapter
    return self.adapter.send_messages(messages)
    
def _enhance_with_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enhance messages with context from DCM."""
    # Implement context enhancement logic
    return enhanced_messages
```

## Framework Core Extension

The Framework Core Application is designed to be extensible and customizable. This section covers how to customize the MessageManager, extend the UI, and implement custom error handling strategies.

### Persona Switching System

Version 2.0.0 introduces a dynamic persona switching system that allows users to switch between different AI personas (e.g., Catalyst, Forge) during a session using the `/persona` command.

#### Architecture

The persona switching system consists of several components:

1. `FrameworkController`: Manages the active persona state and processes the `/persona` command
2. `UIManager`: Updates the UI to reflect the active persona
3. `LIALManager`: Passes the active persona ID to the LLM adapter
4. `ConfigurationManager`: Loads the default persona from configuration

#### Implementation Details

```python
# In FrameworkController
class FrameworkController:
    def __init__(self, config_manager):
        # ...
        self.active_persona_id = None  # Will be set during initialization
        
    def _setup_initial_context(self):
        # Set default persona from config
        framework_settings = self.config_manager.get_framework_settings()
        default_persona = framework_settings.get("default_persona", "catalyst")
        self.active_persona_id = default_persona
        
        # Update UI prefix
        if self.ui_manager:
            persona_display_name = self.active_persona_id.capitalize()
            prefix = f"({persona_display_name}): "
            self.ui_manager.set_assistant_prefix(prefix)
            
    def _process_special_command(self, user_input):
        # ...
        elif command == "/persona":
            # Switch active persona logic
            # Validate persona exists in DCM
            # Update self.active_persona_id
            # Update UI manager prefix
            
    def _process_messages_with_llm(self, messages):
        # Pass active persona to LIAL
        return self.lial_manager.send_messages(messages, active_persona_id=self.active_persona_id)
```

#### Extending the Persona System

To extend the persona system with additional features:

1. **New Personas**: Add new persona documents to your `FRAMEWORK_CONTEXT.md` file
2. **Custom Persona Logic**: Extend the `FrameworkController` class to implement custom persona selection logic
3. **Persona-Specific UI**: Extend the `UIManager` to implement more advanced UI changes based on the active persona

```python
# Example: Adding persona-specific styling to the UI
class EnhancedUIManager(UserInterfaceManager):
    def set_assistant_prefix(self, prefix: str) -> None:
        """Set assistant prefix with persona-specific styling."""
        self.assistant_prefix = prefix
        
        # Extract persona name from prefix (e.g., "(Catalyst): " → "Catalyst")
        persona_name = prefix.strip("(): ")
        
        # Set persona-specific styling
        if persona_name.lower() == "catalyst":
            self.assistant_color = self.COLORS["blue"]
        elif persona_name.lower() == "forge":
            self.assistant_color = self.COLORS["green"]
        else:
            self.assistant_color = self.COLORS["white"]
```

### MessageManager Customization

#### Custom Pruning Strategies

You can implement custom pruning strategies by extending the MessageManager class:

```python
from framework_core.message_manager import MessageManager

class CustomMessageManager(MessageManager):
    """Custom message manager with enhanced pruning."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the custom message manager."""
        super().__init__(config)
        self.pruning_strategy = self.config.get("pruning_strategy", "custom")
        
    def prune_history(self, preserve_system: bool = True) -> None:
        """Custom pruning implementation."""
        if len(self.messages) <= self.max_history_length:
            return
            
        self.logger.info(f"Pruning message history from {len(self.messages)} messages")
        
        if self.pruning_strategy == "custom":
            # Implement custom pruning logic
            # ...
            
        else:
            # Fall back to parent implementation
            super().prune_history(preserve_system)
```

#### Message Transformations

You can implement custom message transformations by overriding the `_format_for_llm` method:

```python
def _format_for_llm(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Custom formatting for LLM consumption."""
    formatted_messages = super()._format_for_llm(messages)
    
    # Apply custom transformations
    for msg in formatted_messages:
        if msg["role"] == "user":
            # Add metadata to user messages
            msg["metadata"] = {"source": "user_input", "timestamp": time.time()}
            
    return formatted_messages
```

### UI Extension Patterns

#### Custom UI Manager

You can create a custom UI Manager by extending the UserInterfaceManager class:

```python
from framework_core.ui_manager import UserInterfaceManager

class CustomUserInterfaceManager(UserInterfaceManager):
    """Custom UI manager with enhanced features."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the custom UI manager."""
        super().__init__(config)
        self.custom_feature_enabled = self.config.get("custom_feature_enabled", False)
        
    def display_assistant_message(self, message: str) -> None:
        """Display an assistant message with custom formatting."""
        if self.custom_feature_enabled:
            # Apply custom formatting
            formatted_message = self._apply_custom_formatting(message)
            # Call parent implementation with formatted message
            super().display_assistant_message(formatted_message)
        else:
            # Use default behavior
            super().display_assistant_message(message)
            
    def _apply_custom_formatting(self, message: str) -> str:
        """Apply custom formatting to a message."""
        # Implement custom formatting logic
        return formatted_message
```

#### UI Plugins

You can implement UI plugins by creating a plugin manager and registering plugins:

```python
class UIPlugin:
    """Base class for UI plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin."""
        self.config = config or {}
        
    def process_message(self, message: str, role: str) -> str:
        """Process a message before display."""
        return message
        
class UIPluginManager:
    """Manager for UI plugins."""
    
    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins = []
        
    def register_plugin(self, plugin: UIPlugin) -> None:
        """Register a plugin."""
        self.plugins.append(plugin)
        
    def process_message(self, message: str, role: str) -> str:
        """Process a message through all plugins."""
        processed_message = message
        for plugin in self.plugins:
            processed_message = plugin.process_message(processed_message, role)
        return processed_message
```

### Error Handling Strategies

#### Custom Error Handler

You can create a custom error handler by extending the ErrorHandler class:

```python
from framework_core.error_handler import ErrorHandler

class CustomErrorHandler(ErrorHandler):
    """Custom error handler with enhanced features."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the custom error handler."""
        super().__init__()
        self.config = config or {}
        self.error_count = {}
        
    def handle_error(self, error_type: str, error_message: str, exception: Optional[Exception] = None) -> str:
        """Handle an error with custom tracking."""
        # Track error count
        self.error_count[error_type] = self.error_count.get(error_type, 0) + 1
        
        # Check if we need special handling based on count
        if self.error_count[error_type] > 3:
            # Special handling for repeated errors
            return self._handle_repeated_error(error_type, error_message, exception)
        
        # Default handling
        return super().handle_error(error_type, error_message, exception)
        
    def _handle_repeated_error(self, error_type: str, error_message: str, exception: Optional[Exception] = None) -> str:
        """Handle a repeated error."""
        # Implement special handling
        return f"Repeated error ({self.error_count[error_type]} occurrences): {error_message}"
```

#### Error Recovery Strategies

You can implement custom error recovery strategies in the Framework Controller:

```python
# In FrameworkController._process_messages_with_llm
def _process_messages_with_llm(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process messages with the LLM with recovery strategy."""
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            self.logger.debug(f"Sending {len(messages)} messages to LLM (attempt {retry_count + 1})")
            llm_response = self.lial_manager.send_messages(messages)
            
            # Validate and sanitize response
            if not isinstance(llm_response, dict):
                self.logger.warning("LLM response is not a dictionary")
                llm_response = {
                    "conversation": "I encountered an issue processing your request. Please try again.",
                    "tool_request": None
                }
                
            return llm_response
            
        except Exception as e:
            retry_count += 1
            self.logger.warning(f"Error processing messages with LLM (attempt {retry_count}): {str(e)}")
            
            if retry_count < max_retries:
                # Implement backoff strategy
                backoff_time = 2 ** retry_count  # Exponential backoff
                self.logger.info(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
            else:
                self.logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                return {
                    "conversation": f"I encountered a persistent error after {max_retries} attempts: {str(e)}",
                    "tool_request": None
                }
```

## Logging and Debugging

The framework includes comprehensive logging and debugging features to help developers diagnose issues.

### Log Format and Levels

The framework uses Python's standard logging module with the following levels:

- `DEBUG`: Detailed debugging information
- `INFO`: General information about normal operation
- `WARNING`: Warnings about potential issues
- `ERROR`: Error conditions that might still allow the framework to continue
- `CRITICAL`: Critical errors that prevent the framework from functioning

#### Log Format

The default log format includes timestamp, level, component name, and message:

```
2025-05-14 10:45:23,456 - INFO - framework_controller - Framework Core Application initialized successfully
```

#### Configuring Logging

Logging is configured in `config.yaml`:

```yaml
framework:
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_file: "framework.log"
```

You can also override the log level with the `FRAMEWORK_LOG_LEVEL` environment variable.

### Debugging Techniques

#### Debug Mode

The framework includes a debug mode that can be enabled with the `/debug` command or in configuration:

```yaml
ui:
  debug_mode: true
```

In debug mode:
- Tool execution results are displayed to the user
- More detailed logging is enabled
- Performance metrics are displayed

#### Component-Specific Debugging

You can enable debug logging for specific components:

```python
# Set up component-specific logger
self.logger = setup_logger("component_name", log_level="DEBUG")
```

#### Accessing Logs

Logs are written to the configured log file and also to the console (if configured). You can access logs programmatically:

```python
import logging

# Get the framework logger
logger = logging.getLogger("framework")

# Get all handlers
handlers = logger.handlers

# Access the most recent log messages
if handlers and hasattr(handlers[0], "buffer"):
    recent_logs = handlers[0].buffer[-10:]  # Last 10 messages
```

### Common Errors and Solutions

Here are some common errors and their solutions:

#### LIALInitError: Failed to initialize adapter

**Possible causes:**
- Missing or invalid API key
- Unsupported LLM provider
- Network connectivity issues

**Solutions:**
- Check API key in configuration or environment variables
- Verify provider spelling in configuration
- Check network connectivity to LLM provider

#### TEPSInitError: Tool handler initialization failed

**Possible causes:**
- Missing or invalid tool settings
- Tool dependencies not installed
- Permission issues

**Solutions:**
- Check tool settings in configuration
- Install required dependencies
- Check file system permissions

#### DCMInitError: Failed to load context definition

**Possible causes:**
- Missing or invalid context definition file
- Referenced documents not found
- Invalid document format

**Solutions:**
- Check context definition path in configuration
- Verify referenced document paths
- Check document format and syntax

#### ToolExecutionError: Permission denied

**Possible causes:**
- User denied permission through ICERC
- Tool trying to access restricted resources
- Insufficient permissions

**Solutions:**
- Grant permission when prompted
- Check tool settings and allowed resources
- Check file system permissions

## Testing

The framework includes a comprehensive testing approach to ensure reliability and correctness.

### Framework Testing Approach

The testing strategy includes:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test the entire framework flow

#### Test Directory Structure

```
tests/
├── unit/
│   ├── framework_core/
│   │   ├── adapters/
│   │   │   └── test_gemini_adapter.py
│   │   ├── test_controller.py
│   │   ├── test_message_manager.py
│   │   └── ...
│   └── ...
├── integration/
│   ├── test_dcm_lial_integration.py
│   ├── test_lial_teps_integration.py
│   └── ...
└── fixtures/
    ├── config/
    │   └── test_config.yaml
    └── ...
```

### Writing Unit Tests

Unit tests focus on testing a single component in isolation. Here's an example of a unit test for the MessageManager:

```python
import unittest
from unittest.mock import patch, MagicMock
from framework_core.message_manager import MessageManager

class TestMessageManager(unittest.TestCase):
    """Unit tests for the MessageManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = {
            "max_length": 10,
            "pruning_strategy": "remove_oldest",
            "prioritize_system_messages": True
        }
        self.message_manager = MessageManager(self.config)
        
    def test_add_system_message(self):
        """Test adding a system message."""
        self.message_manager.add_system_message("Test system message")
        messages = self.message_manager.get_messages()
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "Test system message")
        
    def test_get_messages_with_filtering(self):
        """Test getting messages with role filtering."""
        self.message_manager.add_system_message("System message")
        self.message_manager.add_user_message("User message")
        self.message_manager.add_assistant_message("Assistant message")
        
        # Include only user and assistant messages
        messages = self.message_manager.get_messages(
            include_roles=["user", "assistant"]
        )
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[1]["role"], "assistant")
        
    def test_prune_history(self):
        """Test history pruning."""
        # Add more messages than max_length
        for i in range(15):
            self.message_manager.add_user_message(f"Message {i}")
            
        # Add a system message
        self.message_manager.add_system_message("System message")
        
        # Prune history
        self.message_manager.prune_history(preserve_system=True)
        
        # Check result
        messages = self.message_manager.get_messages()
        self.assertEqual(len(messages), self.config["max_length"])
        
        # System message should be preserved
        system_messages = [m for m in messages if m["role"] == "system"]
        self.assertEqual(len(system_messages), 1)
        
    @patch("time.time")
    def test_message_timestamp(self, mock_time):
        """Test timestamps in messages."""
        mock_time.return_value = 12345.0
        
        self.message_manager.add_user_message("Test message")
        messages = self.message_manager.get_messages()
        
        self.assertEqual(messages[0]["timestamp"], 12345.0)
```

### Writing Integration Tests

Integration tests focus on testing interactions between components. Here's an example of an integration test for DCM and LIAL:

```python
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from framework_core.component_managers.dcm_manager import DCMManager
from framework_core.component_managers.lial_manager import LIALManager

class TestDCMLIALIntegration(unittest.TestCase):
    """Integration tests for DCM and LIAL."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary context definition file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.context_path = os.path.join(self.temp_dir.name, "FRAMEWORK_CONTEXT.md")
        
        with open(self.context_path, "w") as f:
            f.write("""# Framework Context Definition
            
## Initial Prompt

This is the initial prompt for testing.

## Test Section

This is a test section.
""")
        
        # Initialize DCM
        self.dcm_manager = DCMManager(self.context_path)
        self.dcm_manager.initialize()
        
        # Mock LLM adapter
        self.mock_adapter = MagicMock()
        self.mock_adapter.send_messages.return_value = {
            "conversation": "Test response",
            "tool_request": None
        }
        
        # Initialize LIAL with mock adapter
        self.lial_manager = LIALManager(
            llm_provider="test",
            llm_settings={},
            dcm_manager=self.dcm_manager
        )
        self.lial_manager._adapter = self.mock_adapter
        
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
        
    def test_initial_prompt_integration(self):
        """Test that DCM's initial prompt is used in LIAL."""
        # Create a simple message list
        messages = [
            {"role": "user", "content": "Hello, world!"}
        ]
        
        # Send messages via LIAL
        self.lial_manager.send_messages(messages)
        
        # Check that the mock adapter was called with enhanced messages
        call_args = self.mock_adapter.send_messages.call_args[0][0]
        
        # The first message should be a system message with the initial prompt
        self.assertEqual(call_args[0]["role"], "system")
        self.assertEqual(call_args[0]["content"], "This is the initial prompt for testing.")
        
        # The second message should be the user message
        self.assertEqual(call_args[1]["role"], "user")
        self.assertEqual(call_args[1]["content"], "Hello, world!")
```

### Writing End-to-End Tests

End-to-end tests validate the entire framework flow. Here's an example of an end-to-end test:

```python
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from framework_core.config_loader import ConfigurationManager
from framework_core.controller import FrameworkController

class TestEndToEnd(unittest.TestCase):
    """End-to-end tests for the framework."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories and files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        self.config_path = os.path.join(self.temp_dir.name, "config.yaml")
        self.context_path = os.path.join(self.temp_dir.name, "FRAMEWORK_CONTEXT.md")
        
        # Create test config
        with open(self.config_path, "w") as f:
            f.write("""
framework:
  name: "Test Framework"
  version: "1.0.0"
  log_level: "DEBUG"

llm:
  provider: "test"
  test:
    api_key: "test_key"
    model: "test-model"

dcm:
  context_definition_path: "{}"

teps:
  permission_required: true
  allowed_tools: ["file_read"]

message_history:
  max_length: 10
""".format(self.context_path))
        
        # Create test context definition
        with open(self.context_path, "w") as f:
            f.write("""# Framework Context Definition
            
## Initial Prompt

This is the initial prompt for testing.
""")
        
        # Mock UI manager to prevent console interaction
        self.mock_ui_manager_class = patch("framework_core.ui_manager.UserInterfaceManager").start()
        self.mock_ui_manager = self.mock_ui_manager_class.return_value
        self.mock_ui_manager.get_user_input.side_effect = ["Hello, world!", "/quit"]
        
        # Mock LLM adapter to return predictable responses
        self.mock_adapter_class = patch("framework_core.adapters.test_adapter.TestAdapter").start()
        self.mock_adapter = self.mock_adapter_class.return_value
        self.mock_adapter.send_messages.return_value = {
            "conversation": "I'm a test assistant",
            "tool_request": None
        }
        
        # Register the test adapter
        patch("framework_core.lial_core.LIALManager._get_adapter", return_value=self.mock_adapter).start()
        
        # Initialize the framework
        self.config_manager = ConfigurationManager(self.config_path)
        self.controller = FrameworkController(self.config_manager)
        
    def tearDown(self):
        """Clean up after tests."""
        patch.stopall()
        self.temp_dir.cleanup()
        
    def test_framework_initialization(self):
        """Test framework initialization."""
        success = self.controller.initialize()
        self.assertTrue(success)
        
        # Check that components were initialized
        self.assertIsNotNone(self.controller.dcm_manager)
        self.assertIsNotNone(self.controller.lial_manager)
        self.assertIsNotNone(self.controller.teps_manager)
        self.assertIsNotNone(self.controller.message_manager)
        self.assertIsNotNone(self.controller.ui_manager)
        self.assertIsNotNone(self.controller.tool_request_handler)
        
    def test_interaction_flow(self):
        """Test the main interaction flow."""
        # Initialize the framework
        success = self.controller.initialize()
        self.assertTrue(success)
        
        # Run the main loop (should process the mock user inputs)
        self.controller.run()
        
        # Check that the LLM adapter was called
        self.mock_adapter.send_messages.assert_called()
        
        # Check that the assistant message was displayed
        self.mock_ui_manager.display_assistant_message.assert_called_with("I'm a test assistant")
```

### Mocking Strategies

When testing the framework, you'll often need to use mocks to isolate components. Here are some common mocking strategies:

#### Mocking LLM Adapter

```python
@patch("framework_core.adapters.gemini_adapter.GeminiAdapter")
def test_with_mock_adapter(self, mock_adapter_class):
    """Test with a mock LLM adapter."""
    mock_adapter = mock_adapter_class.return_value
    mock_adapter.send_messages.return_value = {
        "conversation": "Mock response",
        "tool_request": None
    }
    
    # Test code using the mock adapter
```

#### Mocking User Input

```python
@patch("framework_core.ui_manager.UserInterfaceManager")
def test_with_mock_ui(self, mock_ui_class):
    """Test with mock user input."""
    mock_ui = mock_ui_class.return_value
    mock_ui.get_user_input.side_effect = ["Hello", "Test", "/quit"]
    
    # Test code using the mock UI
```

#### Mocking File System Operations

```python
@patch("os.path.exists")
@patch("builtins.open", new_callable=unittest.mock.mock_open)
def test_with_mock_fs(self, mock_open, mock_exists):
    """Test with mock file system."""
    mock_exists.return_value = True
    mock_open.return_value.read.return_value = "Test file content"
    
    # Test code using the mock file system
```

## Contribution Guidelines

The Framework Core Application is an open-source project that welcomes contributions from developers. This section outlines the coding standards, pull request process, and documentation requirements.

### Coding Standards

#### Python Style Guide

The framework follows PEP 8 Python style guidelines with the following specifics:

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 88 characters
- **Imports**: Grouped by standard library, third-party, and framework modules
- **Docstrings**: Google style docstrings
- **Type Hints**: Use type hints throughout the codebase
- **Exception Handling**: Specific exception types, no bare `except`

Example:

```python
from typing import Dict, List, Any, Optional
import json
import time

from third_party_lib import SomeClass

from framework_core.exceptions import FrameworkError
from framework_core.utils.logging_utils import setup_logger


class ExampleClass:
    """
    Example class demonstrating coding standards.
    
    This class shows the proper formatting, docstrings, and typing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the example class.
        
        Args:
            config: Optional configuration dictionary
        """
        self.logger = setup_logger("example_class")
        self.config = config or {}
        
    def process_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process data according to configuration.
        
        Args:
            data: List of data items to process
            
        Returns:
            Processed data result
            
        Raises:
            FrameworkError: If processing fails
        """
        try:
            self.logger.debug(f"Processing {len(data)} items")
            
            # Processing logic
            result = {"processed_items": len(data), "status": "success"}
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            raise FrameworkError(f"Data processing failed: {str(e)}")
```

#### Code Organization

- **Single Responsibility**: Each module and class should have a single responsibility
- **Consistent Naming**: Use descriptive names that follow Python conventions
- **Error Handling**: Centralized error handling through the `ErrorHandler`
- **Logging**: Use the provided logging utilities for all log messages
- **Configuration**: Use the configuration system for all settings

### Pull Request Process

1. **Fork the Repository**: Create a fork of the main repository
2. **Create a Branch**: Create a branch for your feature or bugfix
3. **Implement Changes**: Make your changes following coding standards
4. **Write Tests**: Add tests for your changes
5. **Update Documentation**: Update relevant documentation
6. **Submit Pull Request**: Submit a pull request with a clear description of changes
7. **Code Review**: Address any feedback from code review
8. **Merge**: Once approved, the PR will be merged

#### PR Description Template

```markdown
## Description

[Describe the changes you've made]

## Issue

[Link to the issue this PR addresses, if applicable]

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Enhancement
- [ ] Documentation update
- [ ] Refactoring

## Testing

- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Tested manually

## Checklist

- [ ] My code follows the coding standards
- [ ] I have updated the documentation
- [ ] All tests pass
- [ ] I have added tests that prove my fix/feature works
```

### Documentation Requirements

All contributions must include appropriate documentation:

#### Code Documentation

- **Module Docstrings**: Each module should have a docstring describing its purpose
- **Class Docstrings**: Each class should have a docstring describing its purpose and usage
- **Method Docstrings**: Each method should have a docstring with parameters, return values, and exceptions
- **Type Hints**: All functions and methods should include type hints

#### User Documentation

- **API Reference**: Update `api_reference.md` for new classes or methods
- **Developer Guide**: Update relevant sections in `DEVELOPER_GUIDE_V2.md`
- **User Guide**: Update user guides if the behavior changes

#### Example Documentation

For new features, provide examples of how to use the feature in the developer guide.

---

This developer guide provides a comprehensive overview of the Framework Core Application's architecture, components, and extension points. By following these guidelines, you can effectively understand, use, and extend the framework for your specific needs.

If you have questions or need additional information, please refer to the API reference or contact the project maintainers.