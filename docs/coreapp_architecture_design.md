# Framework Core Application Architecture Design

## 1. Overview

The Framework Core Application serves as the main orchestrator for the AI-Assisted Framework V2, integrating the LIAL (LLM Interaction Abstraction Layer), TEPS (Tool Execution & Permission Service), and DCM (Dynamic Context Manager) components. This document defines the detailed architecture of the Core Application, including class structures, interaction patterns, error handling strategies, and implementation guidelines.

## 2. Architecture Principles

The Framework Core Application architecture is guided by the following principles:

1. **Separation of Concerns**: Each component has clearly defined responsibilities with minimal overlap.
2. **Dependency Inversion**: High-level modules do not depend on low-level modules. Both depend on abstractions.
3. **Single Responsibility**: Each class has a single responsibility and reason to change.
4. **Open/Closed**: Components are open for extension but closed for modification.
5. **Loose Coupling**: Components interact through well-defined interfaces.
6. **Error Resilience**: The system can recover from component failures and API errors.
7. **Configurability**: Behavior can be customized through external configuration.

## 3. Component Overview

The Framework Core Application consists of the following main components:

1. **Framework Controller**: The central orchestrator that manages the interaction flow and component lifecycle.
2. **Configuration Manager**: Handles loading, validation, and access to configuration settings.
3. **Message Manager**: Maintains the conversation history and handles message pruning.
4. **Tool Request Handler**: Processes tool requests and manages the tool execution flow.
5. **User Interface Manager**: Handles user input and output formatting.
6. **Component Integration Interfaces**: Abstract interfaces for interacting with LIAL, TEPS, and DCM.

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Framework Core Application                       │
│                                                                     │
│  ┌─────────────────┐      ┌─────────────────┐    ┌──────────────┐   │
│  │                 │      │                 │    │              │   │
│  │  Configuration  │      │   Framework     │    │    Message   │   │
│  │    Manager      │◄────►│   Controller    │◄──►│    Manager   │   │
│  │                 │      │                 │    │              │   │
│  └─────────────────┘      └───────┬─────────┘    └──────────────┘   │
│                                   │                                  │
│                                   │                                  │
│  ┌─────────────────┐      ┌───────▼─────────┐    ┌──────────────┐   │
│  │                 │      │                 │    │              │   │
│  │  User Interface │◄────►│  Tool Request   │    │ Error Handler│   │
│  │    Manager      │      │    Handler      │    │              │   │
│  │                 │      │                 │    │              │   │
│  └─────────────────┘      └─────────────────┘    └──────────────┘   │
│                                                                     │
└──────────┬─────────────────────┬────────────────────┬──────────────┘
           │                     │                    │
           ▼                     ▼                    ▼
┌─────────────────┐    ┌─────────────────┐   ┌─────────────────┐
│                 │    │                 │   │                 │
│       DCM       │    │      LIAL       │   │      TEPS       │
│                 │    │                 │   │                 │
└─────────────────┘    └─────────────────┘   └─────────────────┘
```

## 4. Detailed Class Structure

### 4.1 Framework Controller

The Framework Controller is the central orchestrator of the application.

```python
class FrameworkController:
    """
    Central orchestrator of the Framework Core Application.
    Manages component initialization, interaction flow, and lifecycle.
    """
    
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize the Framework Controller with configuration."""
        self.config_manager = config_manager
        self.message_manager = None
        self.dcm_manager = None
        self.lial_manager = None
        self.teps_manager = None
        self.ui_manager = None
        self.tool_request_handler = None
        self.error_handler = ErrorHandler()
        self.running = False
        
    def initialize(self) -> bool:
        """Initialize all framework components."""
        try:
            # Initialize components in dependency order
            self.dcm_manager = self._initialize_dcm()
            self.lial_manager = self._initialize_lial()
            self.teps_manager = self._initialize_teps()
            self.message_manager = MessageManager()
            self.ui_manager = UserInterfaceManager()
            self.tool_request_handler = ToolRequestHandler(self.teps_manager)
            
            # Set up initial context
            self._setup_initial_context()
            return True
        except Exception as e:
            self.error_handler.handle_error("Initialization Error", str(e))
            return False
    
    def _initialize_dcm(self) -> DCMManager:
        """Initialize the DCM component."""
        # Implementation details
        
    def _initialize_lial(self) -> LIALManager:
        """Initialize the LIAL component with the appropriate adapter."""
        # Implementation details
        
    def _initialize_teps(self) -> TEPSManager:
        """Initialize the TEPS component."""
        # Implementation details
    
    def _setup_initial_context(self) -> None:
        """Set up the initial context and prompt."""
        # Implementation details
        
    def run(self) -> None:
        """Run the main interaction loop."""
        self.running = True
        
        # Send initial prompt
        initial_prompt = self.dcm_manager.get_initial_prompt()
        self.message_manager.add_system_message(initial_prompt)
        
        # Main interaction loop
        while self.running:
            try:
                # Send messages to LLM
                response = self._process_messages_with_llm()
                
                # Handle tool requests if present
                if response.has_tool_request():
                    self._handle_tool_request(response.get_tool_request())
                
                # Display conversation to user
                self.ui_manager.display_assistant_message(response.get_conversation())
                
                # Get user input
                user_input = self.ui_manager.get_user_input()
                
                # Process special commands (e.g., /quit)
                if self._process_special_command(user_input):
                    continue
                
                # Add user message to history
                self.message_manager.add_user_message(user_input)
            
            except Exception as e:
                self.error_handler.handle_error("Runtime Error", str(e))
    
    def _process_messages_with_llm(self) -> LLMResponse:
        """Process messages with the LLM via LIAL."""
        # Implementation details
        
    def _handle_tool_request(self, tool_request: ToolRequest) -> None:
        """Handle a tool request via the Tool Request Handler."""
        # Implementation details
        
    def _process_special_command(self, user_input: str) -> bool:
        """Process special commands (e.g., /quit)."""
        # Implementation details
        
    def shutdown(self) -> None:
        """Perform graceful shutdown."""
        self.running = False
        # Cleanup resources
```

### 4.2 Configuration Manager

Handles loading, validation, and access to configuration settings.

```python
class ConfigurationManager:
    """
    Manages loading, validation, and access to configuration settings.
    """
    
    def __init__(self, config_path: str = None, cmd_args: Dict[str, Any] = None):
        """Initialize the Configuration Manager."""
        self.config_path = config_path or self._find_default_config()
        self.cmd_args = cmd_args or {}
        self.config_data = {}
        
    def load_configuration(self) -> bool:
        """Load and validate configuration from file."""
        try:
            self._load_from_file()
            self._override_with_cmd_args()
            self._validate_configuration()
            self._expand_environment_variables()
            return True
        except Exception as e:
            raise ConfigError(f"Configuration error: {str(e)}")
            
    def _load_from_file(self) -> None:
        """Load configuration from YAML file."""
        # Implementation details
        
    def _override_with_cmd_args(self) -> None:
        """Override configuration with command-line arguments."""
        # Implementation details
        
    def _validate_configuration(self) -> None:
        """Validate required configuration settings."""
        # Implementation details
        
    def _expand_environment_variables(self) -> None:
        """Expand environment variables in configuration values."""
        # Implementation details
        
    def _find_default_config(self) -> str:
        """Find the default configuration file path."""
        # Implementation details
        
    def get_llm_provider(self) -> str:
        """Get the configured LLM provider."""
        return self.config_data.get("llm_provider")
    
    def get_context_definition_path(self) -> str:
        """Get the path to the context definition file."""
        return self.config_data.get("context_definition_file")
    
    def get_llm_settings(self, provider: str = None) -> Dict[str, Any]:
        """Get LLM-specific settings."""
        provider = provider or self.get_llm_provider()
        return self.config_data.get("llm_settings", {}).get(provider, {})
    
    def get_teps_settings(self) -> Dict[str, Any]:
        """Get TEPS-specific settings."""
        return self.config_data.get("teps_settings", {})
    
    def get_logging_level(self) -> str:
        """Get the configured logging level."""
        return self.config_data.get("logging", {}).get("level", "INFO")
```

### 4.3 Message Manager

Manages the conversation history and handles message pruning.

```python
class MessageManager:
    """
    Manages conversation history and provides message pruning capabilities.
    """
    
    def __init__(self, max_history_length: int = 100):
        """Initialize the Message Manager."""
        self.messages = []
        self.max_history_length = max_history_length
        
    def add_system_message(self, content: str) -> None:
        """Add a system message to the conversation history."""
        self.messages.append({
            "role": "system",
            "content": content
        })
        
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        self.messages.append({
            "role": "user",
            "content": content
        })
        
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history."""
        self.messages.append({
            "role": "assistant",
            "content": content
        })
        
    def add_tool_result_message(self, tool_name: str, content: str, tool_call_id: str) -> None:
        """Add a tool result message to the conversation history."""
        self.messages.append({
            "role": "tool_result",
            "content": content,
            "tool_name": tool_name,
            "tool_call_id": tool_call_id
        })
        
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the conversation history."""
        return self.messages
    
    def prune_history(self, preserve_system: bool = True) -> None:
        """
        Prune the message history to prevent context window overflow.
        Optionally preserve system messages.
        """
        # Implementation details
        
    def clear_history(self, preserve_system: bool = True) -> None:
        """
        Clear the message history.
        Optionally preserve system messages.
        """
        if preserve_system:
            self.messages = [msg for msg in self.messages if msg["role"] == "system"]
        else:
            self.messages = []
```

### 4.4 Tool Request Handler

Processes tool requests and manages the tool execution flow via TEPS.

```python
class ToolRequestHandler:
    """
    Processes tool requests and manages tool execution flow via TEPS.
    """
    
    def __init__(self, teps_manager: TEPSManager):
        """Initialize the Tool Request Handler."""
        self.teps_manager = teps_manager
        
    def process_tool_request(self, tool_request: ToolRequest) -> ToolResult:
        """
        Process a tool request via TEPS.
        
        Args:
            tool_request: The tool request to process.
            
        Returns:
            A ToolResult containing the result of the tool execution.
        """
        # Validate the tool request
        self._validate_tool_request(tool_request)
        
        # Execute the tool via TEPS
        tool_result = self.teps_manager.execute_tool(tool_request)
        
        return tool_result
    
    def _validate_tool_request(self, tool_request: ToolRequest) -> None:
        """Validate a tool request before processing."""
        # Implementation details
        
    def format_tool_result_as_message(self, tool_result: ToolResult) -> Dict[str, Any]:
        """Format a tool result as a message for the conversation history."""
        return {
            "role": "tool_result",
            "content": json.dumps(tool_result.get("data")),
            "tool_name": tool_result.get("tool_name"),
            "tool_call_id": tool_result.get("request_id")
        }
```

### 4.5 User Interface Manager

Handles user input and output formatting.

```python
class UserInterfaceManager:
    """
    Manages user interface interactions, including input/output and formatting.
    """
    
    def __init__(self, input_handler=None, output_handler=None):
        """Initialize the User Interface Manager."""
        self.input_handler = input_handler or self._default_input_handler
        self.output_handler = output_handler or self._default_output_handler
        
    def display_assistant_message(self, message: str) -> None:
        """Display an assistant message to the user."""
        formatted_message = self._format_assistant_message(message)
        self.output_handler(formatted_message)
        
    def display_system_message(self, message: str) -> None:
        """Display a system message to the user."""
        formatted_message = self._format_system_message(message)
        self.output_handler(formatted_message)
        
    def display_error_message(self, error_type: str, error_message: str) -> None:
        """Display an error message to the user."""
        formatted_message = self._format_error_message(error_type, error_message)
        self.output_handler(formatted_message)
        
    def get_user_input(self, prompt: str = "> ") -> str:
        """Get input from the user."""
        return self.input_handler(prompt)
    
    def _format_assistant_message(self, message: str) -> str:
        """Format an assistant message for display."""
        # Implementation details
        
    def _format_system_message(self, message: str) -> str:
        """Format a system message for display."""
        # Implementation details
        
    def _format_error_message(self, error_type: str, error_message: str) -> str:
        """Format an error message for display."""
        # Implementation details
        
    def _default_input_handler(self, prompt: str) -> str:
        """Default input handler implementation."""
        return input(prompt)
    
    def _default_output_handler(self, message: str) -> None:
        """Default output handler implementation."""
        print(message)
```

### 4.6 Component Integration Managers

Abstract interfaces for interacting with the external components.

#### 4.6.1 DCM Manager

```python
class DCMManager:
    """
    Manages interaction with the Dynamic Context Manager (DCM) component.
    """
    
    def __init__(self, context_definition_path: str):
        """Initialize the DCM Manager."""
        self.context_definition_path = context_definition_path
        self.dcm_instance = None
        
    def initialize(self) -> bool:
        """Initialize the DCM component."""
        try:
            from framework_core.dcm import DynamicContextManager
            self.dcm_instance = DynamicContextManager(self.context_definition_path)
            return True
        except Exception as e:
            raise ComponentInitError(f"Failed to initialize DCM: {str(e)}")
            
    def get_initial_prompt(self) -> str:
        """Get the initial prompt template from DCM."""
        # Implementation details
        
    def get_full_context(self) -> Dict[str, Any]:
        """Get the full context loaded by DCM."""
        # Implementation details
        
    def get_document_content(self, doc_id: str) -> str:
        """Get the content of a specific document from DCM."""
        # Implementation details
        
    def get_persona_definitions(self) -> Dict[str, Any]:
        """Get all persona definitions from DCM."""
        # Implementation details
```

#### 4.6.2 LIAL Manager

```python
class LIALManager:
    """
    Manages interaction with the LLM Interaction Abstraction Layer (LIAL) component.
    """
    
    def __init__(self, llm_provider: str, llm_settings: Dict[str, Any], dcm_manager: DCMManager):
        """Initialize the LIAL Manager."""
        self.llm_provider = llm_provider
        self.llm_settings = llm_settings
        self.dcm_manager = dcm_manager
        self.adapter_instance = None
        
    def initialize(self) -> bool:
        """Initialize the LIAL adapter."""
        try:
            adapter_class = self._get_adapter_class()
            self.adapter_instance = adapter_class(
                config=self.llm_settings,
                dcm_instance=self.dcm_manager.dcm_instance
            )
            return True
        except Exception as e:
            raise ComponentInitError(f"Failed to initialize LIAL: {str(e)}")
            
    def _get_adapter_class(self):
        """Get the appropriate adapter class based on the provider."""
        if self.llm_provider == "gemini_2_5_pro":
            from framework_core.adapters.gemini_adapter import GeminiAdapter
            return GeminiAdapter
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
            
    def send_messages(self, messages: List[Dict[str, Any]], active_persona_id: str = None) -> Dict[str, Any]:
        """
        Send messages to the LLM via the LIAL adapter.
        
        Args:
            messages: List of messages to send.
            active_persona_id: Optional ID of the active persona.
            
        Returns:
            LLMResponse object with conversation and optional tool request.
        """
        # Implementation details
```

#### 4.6.3 TEPS Manager

```python
class TEPSManager:
    """
    Manages interaction with the Tool Execution & Permission Service (TEPS) component.
    """
    
    def __init__(self, teps_settings: Dict[str, Any]):
        """Initialize the TEPS Manager."""
        self.teps_settings = teps_settings
        self.teps_instance = None
        
    def initialize(self) -> bool:
        """Initialize the TEPS component."""
        try:
            from framework_core.teps import TEPSEngine
            self.teps_instance = TEPSEngine(config=self.teps_settings)
            return True
        except Exception as e:
            raise ComponentInitError(f"Failed to initialize TEPS: {str(e)}")
            
    def execute_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool via TEPS.
        
        Args:
            tool_request: The tool request to execute.
            
        Returns:
            ToolResult object with the result of the tool execution.
        """
        # Implementation details
```

### 4.7 Error Handler

Centralized error handling and logging.

```python
class ErrorHandler:
    """
    Provides centralized error handling and logging.
    """
    
    def __init__(self, logger=None):
        """Initialize the Error Handler."""
        self.logger = logger or self._setup_default_logger()
        
    def handle_error(self, error_type: str, error_message: str, exception: Exception = None) -> None:
        """
        Handle an error by logging it and returning a formatted error message.
        
        Args:
            error_type: The type of error.
            error_message: The error message.
            exception: Optional exception object.
            
        Returns:
            Formatted error message for display.
        """
        # Log the error
        if exception:
            self.logger.error(f"{error_type}: {error_message}", exc_info=exception)
        else:
            self.logger.error(f"{error_type}: {error_message}")
            
        return f"{error_type}: {error_message}"
    
    def _setup_default_logger(self):
        """Set up the default logger."""
        # Implementation details
```

## 5. Interaction Sequences

### 5.1 Initialization Sequence

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│               │      │               │      │               │      │               │
│  run_framework│      │ Configuration │      │  Framework    │      │  DCM Manager  │
│               │      │   Manager     │      │  Controller   │      │               │
│               │      │               │      │               │      │               │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │                      │
        │  1. Create           │                      │                      │
        │─────────────────────>│                      │                      │
        │                      │                      │                      │
        │                      │  2. Load Config      │                      │
        │                      │────────────────────> │                      │
        │                      │                      │                      │
        │                      │  3. Return Config    │                      │
        │                      │<────────────────────┐│                      │
        │                      │                      │                      │
        │                      │                      │  4. Create           │
        │                      │                      │─────────────────────>│
        │                      │                      │                      │
        │                      │                      │  5. Initialize DCM   │
        │                      │                      │─────────────────────>│
        │                      │                      │                      │
        │                      │                      │  6. Return Success   │
        │                      │                      │<─────────────────────│
        │                      │                      │                      │
┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐
│               │      │               │      │               │      │               │
│  run_framework│      │ Configuration │      │  Framework    │      │  DCM Manager  │
│               │      │   Manager     │      │  Controller   │      │               │
│               │      │               │      │               │      │               │
└───────────────┘      └───────────────┘      └───────┬───────┘      └───────────────┘
                                                      │
                                                      │
                                                      │
                                                      ▼
┌───────────────┐                            ┌───────────────┐      ┌───────────────┐
│               │                            │               │      │               │
│ LIAL Manager  │                            │ TEPS Manager  │      │     Other     │
│               │                            │               │      │  Components   │
│               │                            │               │      │               │
└───────┬───────┘                            └───────┬───────┘      └───────┬───────┘
        │                                            │                      │
        │  7. Initialize LIAL                        │                      │
        │<────────────────────────────────────────────                      │
        │                                            │                      │
        │  8. Return Success                         │                      │
        │────────────────────────────────────────────>                      │
        │                                            │                      │
        │                                            │  9. Initialize TEPS  │
        │                                            │<─────────────────────│
        │                                            │                      │
        │                                            │  10. Return Success  │
        │                                            │─────────────────────>│
┌───────┴───────┐                            ┌───────┴───────┐      ┌───────┴───────┐
│               │                            │               │      │               │
│ LIAL Manager  │                            │ TEPS Manager  │      │     Other     │
│               │                            │               │      │  Components   │
│               │                            │               │      │               │
└───────────────┘                            └───────────────┘      └───────────────┘
```

### 5.2 Main Interaction Loop Sequence

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│               │      │               │      │               │      │               │
│  Framework    │      │  Message      │      │  LIAL Manager │      │  UI Manager   │
│  Controller   │      │  Manager      │      │               │      │               │
│               │      │               │      │               │      │               │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │                      │
        │  1. Get Messages     │                      │                      │
        │─────────────────────>│                      │                      │
        │                      │                      │                      │
        │  2. Return Messages  │                      │                      │
        │<─────────────────────│                      │                      │
        │                      │                      │                      │
        │  3. Send Messages    │                      │                      │
        │─────────────────────────────────────────────>                      │
        │                      │                      │                      │
        │  4. Return Response  │                      │                      │
        │<─────────────────────────────────────────────                      │
        │                      │                      │                      │
        │  5. Display Response │                      │                      │
        │─────────────────────────────────────────────────────────────────>│
        │                      │                      │                      │
        │  6. Get User Input   │                      │                      │
        │─────────────────────────────────────────────────────────────────>│
        │                      │                      │                      │
        │  7. Return User Input│                      │                      │
        │<─────────────────────────────────────────────────────────────────│
        │                      │                      │                      │
        │  8. Add User Message │                      │                      │
        │─────────────────────>│                      │                      │
        │                      │                      │                      │
┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐
│               │      │               │      │               │      │               │
│  Framework    │      │  Message      │      │  LIAL Manager │      │  UI Manager   │
│  Controller   │      │  Manager      │      │               │      │               │
│               │      │               │      │               │      │               │
└───────────────┘      └───────────────┘      └───────────────┘      └───────────────┘
```

### 5.3 Tool Execution Sequence

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│               │      │ Tool Request  │      │ TEPS Manager  │      │  Message      │
│  Framework    │      │   Handler     │      │               │      │  Manager      │
│  Controller   │      │               │      │               │      │               │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │                      │
        │  1. Process Tool Req │                      │                      │
        │─────────────────────>│                      │                      │
        │                      │                      │                      │
        │                      │  2. Execute Tool     │                      │
        │                      │─────────────────────>│                      │
        │                      │                      │                      │
        │                      │  3. Return Result    │                      │
        │                      │<─────────────────────│                      │
        │                      │                      │                      │
        │  4. Return Result    │                      │                      │
        │<─────────────────────│                      │                      │
        │                      │                      │                      │
        │  5. Format as Message│                      │                      │
        │─────────────────────>│                      │                      │
        │                      │                      │                      │
        │  6. Return Message   │                      │                      │
        │<─────────────────────│                      │                      │
        │                      │                      │                      │
        │  7. Add Tool Result  │                      │                      │
        │───────────────────────────────────────────────────────────────────>│
        │                      │                      │                      │
┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐      ┌───────┴───────┐
│               │      │ Tool Request  │      │ TEPS Manager  │      │  Message      │
│  Framework    │      │   Handler     │      │               │      │  Manager      │
│  Controller   │      │               │      │               │      │               │
└───────────────┘      └───────────────┘      └───────────────┘      └───────────────┘
```

## 6. Error Handling Strategy

### 6.1 Error Categories

1. **Initialization Errors**: Errors that occur during component initialization.
2. **Configuration Errors**: Errors related to configuration loading or validation.
3. **Runtime Errors**: Errors that occur during the main interaction loop.
4. **LLM API Errors**: Errors related to communication with the LLM API.
5. **TEPS Errors**: Errors related to tool execution.
6. **User Input Errors**: Errors related to processing user input.

### 6.2 Error Handling Approach

1. **Centralized Error Handler**: All errors are routed through the ErrorHandler class.
2. **Consistent Logging**: All errors are logged with appropriate severity levels.
3. **User-Friendly Messages**: Error messages are formatted for user readability.
4. **Graceful Degradation**: Non-fatal errors allow the application to continue with reduced functionality.
5. **Automatic Recovery**: Automatic retry for transient errors (e.g., network issues).

### 6.3 Exception Hierarchy

```
BaseException
└── Exception
    └── FrameworkError                # Base exception for all framework errors
        ├── ConfigError               # Configuration-related errors
        ├── ComponentInitError        # Component initialization errors
        │   ├── DCMInitError          # DCM-specific initialization errors
        │   ├── LIALInitError         # LIAL-specific initialization errors
        │   └── TEPSInitError         # TEPS-specific initialization errors
        ├── LLMAPIError               # Errors communicating with LLM API
        ├── ToolExecutionError        # Errors during tool execution
        └── UserInputError            # Errors processing user input
```

### 6.4 Error Recovery Strategies

| Error Type | Recovery Strategy |
|------------|-------------------|
| Configuration | Fall back to default configuration when possible |
| DCM Initialization | Provide minimal context and continue |
| LIAL Communication | Retry with exponential backoff, then alert user |
| TEPS Execution | Report error, continue with conversation |
| User Input | Request corrected input |

## 7. Configuration System Design

### 7.1 Configuration Sources

1. **Default Values**: Hardcoded defaults for non-critical settings.
2. **Configuration File**: YAML file with all configurable settings.
3. **Command Line Arguments**: Override file-based settings.
4. **Environment Variables**: Used for sensitive data like API keys.

### 7.2 Configuration File Structure

```yaml
# Basic Settings
llm_provider: "gemini_2_5_pro"  # Identifies which LIAL adapter to use
api_key_env_var: "GEMINI_API_KEY"  # Environment variable name for the API key
context_definition_file: "./config/FRAMEWORK_CONTEXT.md"  # Path to context definition

# LLM Provider Specific Settings
llm_settings:
  gemini_2_5_pro:
    model_name: "gemini-1.5-pro-latest"
    temperature: 0.7
    max_output_tokens: 8192
    top_k: 40
    top_p: 0.95

# TEPS Settings
teps_settings:
  allowlist_file: ".project_teps_allowlist.json"
  default_confirmation: false
  remember_confirmations: true

# Logging Configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "framework.log"  # Set to null for console only

# Message History Settings
message_history:
  max_length: 100
  prioritize_system_messages: true
  pruning_strategy: "remove_oldest"  # remove_oldest, summarize

# User Interface Settings
ui:
  input_prompt: "> "
  assistant_prefix: "(AI): "
  system_prefix: "[System]: "
  error_prefix: "[Error]: "
```

### 7.3 Environment Variables

Sensitive information like API keys should be stored in environment variables:

- `GEMINI_API_KEY`: For Gemini API access
- `FRAMEWORK_CONFIG_PATH`: Optional override for config file path
- `FRAMEWORK_LOG_LEVEL`: Optional override for log level

## 8. Extensibility Design

### 8.1 Extension Points

1. **LLM Adapters**: New LLM providers can be supported by adding new adapter classes.
2. **User Interface**: The UI layer can be extended or replaced with alternative implementations.
3. **Tool Handling**: New tools can be added through the TEPS component.
4. **Message Processors**: Pipeline for pre/post-processing messages.

### 8.2 Adding New LLM Adapters

To add support for a new LLM provider:

1. Create a new adapter class in `framework_core/adapters/`
2. Implement the required interface methods
3. Register the adapter in the LIALManager's `_get_adapter_class` method
4. Add provider-specific configuration options to the config schema

```python
# Example of adding a new adapter
class NewProviderAdapter:
    """Adapter for New LLM Provider."""
    
    def __init__(self, config: Dict[str, Any], dcm_instance: Any):
        """Initialize the adapter."""
        self.config = config
        self.dcm_instance = dcm_instance
        self.client = self._initialize_client()
        
    def _initialize_client(self):
        """Initialize the provider-specific client."""
        # Implementation details
        
    def send_message_sequence(self, messages: List[Dict[str, Any]], active_persona_id: str = None) -> Dict[str, Any]:
        """Send a sequence of messages to the LLM."""
        # Implementation details
```

### 8.3 Configuration for Extensions

Extensions can define their own configuration sections in the YAML config file:

```yaml
extensions:
  new_llm_provider:
    api_key_env_var: "NEW_PROVIDER_API_KEY"
    endpoint_url: "https://api.newprovider.com/v1"
    timeout_seconds: 30
```

## 9. Implementation Guidelines

### 9.1 Code Organization

```
/
├── run_framework.py                   # Main entry point
├── framework_core/                    # Core package
│   ├── __init__.py
│   ├── config_loader.py               # Configuration management
│   ├── controller.py                  # Framework controller
│   ├── message_manager.py             # Message handling
│   ├── tool_request_handler.py        # Tool request processing
│   ├── ui_manager.py                  # User interface management
│   ├── error_handler.py               # Error handling
│   ├── exceptions.py                  # Exception definitions
│   ├── component_managers/            # Component integration
│   │   ├── __init__.py
│   │   ├── dcm_manager.py
│   │   ├── lial_manager.py
│   │   └── teps_manager.py
│   └── utils/                         # Utility functions
│       ├── __init__.py
│       ├── logging_utils.py
│       └── message_utils.py
├── tests/                             # Test suite
│   ├── unit/
│   │   ├── test_config_loader.py
│   │   ├── test_controller.py
│   │   └── ...
│   └── integration/
│       └── test_framework_core_integration.py
└── docs/                              # Documentation
    └── core_app_implementation.md
```

### 9.2 Best Practices

1. **Type Hints**: Use Python type hints throughout the codebase.
2. **Documentation**: Include comprehensive docstrings for all classes and methods.
3. **Error Handling**: Use try-except blocks with specific exception types.
4. **Logging**: Use the logging module with appropriate levels.
5. **Testing**: Write tests for all components and main code paths.
6. **Separation of Concerns**: Keep components focused on their specific responsibilities.
7. **Dependency Injection**: Use dependency injection to improve testability.

### 9.3 Performance Considerations

1. **Message Pruning**: Implement efficient message pruning to manage context window size.
2. **Lazy Loading**: Load components only when needed.
3. **Resource Management**: Properly manage connections and resources.
4. **Async Support**: Consider async support for non-blocking operations.

## 10. Testing Approach

### 10.1 Unit Testing

Unit tests should cover individual classes and methods:

- ConfigurationManager tests
- FrameworkController tests
- MessageManager tests
- ToolRequestHandler tests
- UIManager tests

### 10.2 Integration Testing

Integration tests should verify interactions between components:

- End-to-end initialization sequence
- Message flow from user input to LLM response
- Tool execution flow
- Error handling scenarios

### 10.3 Mocking Strategy

Mock external components to isolate testing:

- Mock DCM, LIAL, and TEPS interfaces
- Mock LLM responses
- Mock user input/output

## 11. Conclusion

This architecture design provides a comprehensive blueprint for implementing the Framework Core Application. It defines the class structure, interaction patterns, error handling strategies, and implementation guidelines necessary to create a robust, maintainable, and extensible application that effectively integrates the LIAL, TEPS, and DCM components.

The design follows the principles outlined in the AI-Assisted Dev Bible, with particular attention to:

1. **Security Considerations**: Clear separation of responsibilities and secure handling of sensitive data.
2. **Testing Frameworks**: Comprehensive testing approach with unit and integration tests.
3. **Documentation Practices**: Detailed documentation of architecture, interfaces, and implementation guidelines.
4. **Strategies for the "70% Problem"**: Well-defined interfaces and error handling strategies to address edge cases.

Next steps include implementing this design according to the phased implementation plan outlined in the RFI document.