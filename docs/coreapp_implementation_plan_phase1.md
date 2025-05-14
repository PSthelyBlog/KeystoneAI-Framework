# Implementation Plan: Framework Core Application - Phase 1

**Date:** 2025-05-13  
**Plan ID:** IMPL-COREAPP-PHASE1  
**Related RFI:** RFI-COREAPP-IMPL-001  
**Author:** Catalyst

## 1. Overview

This implementation plan provides a detailed, step-by-step approach for implementing Phase 1 of the Framework Core Application, focusing on the core structure and initialization components as outlined in RFI-COREAPP-IMPL-001. The plan breaks down the work into logical steps, each with specific tasks, dependencies, and implementation guidelines.

## 2. Implementation Steps

### Step 1: Project Structure Setup (Foundation)

**Objective:** Establish the basic directory structure and package framework.

**Tasks:**

1. Create directory structure:
   ```
   /
   ├── run_framework.py                   # Main entry point
   ├── framework_core/                    # Core package
   │   ├── __init__.py
   │   ├── config_loader.py               # Configuration management
   │   ├── controller.py                  # Framework controller
   │   ├── error_handler.py               # Error handling
   │   ├── exceptions.py                  # Exception definitions
   │   ├── component_managers/            # Component integration
   │   │   ├── __init__.py
   │   │   ├── dcm_manager.py
   │   │   ├── lial_manager.py
   │   │   └── teps_manager.py
   │   └── utils/                         # Utility functions
   │       ├── __init__.py
   │       └── logging_utils.py
   ```

2. Create the base package with meaningful imports:
   ```python
   # framework_core/__init__.py
   """
   Framework Core Application - Central orchestration for AI-Assisted Framework V2.
   
   This package integrates the LIAL, TEPS, and DCM components into a cohesive application.
   """

   __version__ = "0.1.0"
   ```

3. Create the utils package:
   ```python
   # framework_core/utils/__init__.py
   """
   Utility functions for the Framework Core Application.
   """
   ```

4. Create the component_managers package:
   ```python
   # framework_core/component_managers/__init__.py
   """
   Component manager interfaces for DCM, LIAL, and TEPS integration.
   """
   ```

**Dependencies:** None - This is the starting point

**Time Estimate:** 30 minutes

---

### Step 2: Exception Hierarchy Implementation

**Objective:** Implement the exception hierarchy to enable robust error handling.

**Tasks:**

1. Create the exceptions.py file with the following structure:
   ```python
   """
   Exception hierarchy for the Framework Core Application.
   
   This module defines all the custom exceptions used throughout the application.
   """
   
   class FrameworkError(Exception):
       """Base exception for all framework errors."""
       pass
   
   class ConfigError(FrameworkError):
       """Configuration-related errors."""
       pass
   
   class ComponentInitError(FrameworkError):
       """Component initialization errors."""
       pass
   
   class DCMInitError(ComponentInitError):
       """DCM-specific initialization errors."""
       pass
   
   class LIALInitError(ComponentInitError):
       """LIAL-specific initialization errors."""
       pass
   
   class TEPSInitError(ComponentInitError):
       """TEPS-specific initialization errors."""
       pass
   
   class LLMAPIError(FrameworkError):
       """Errors communicating with LLM API."""
       pass
   
   class ToolExecutionError(FrameworkError):
       """Errors during tool execution."""
       pass
   
   class UserInputError(FrameworkError):
       """Errors processing user input."""
       pass
   ```

**Dependencies:** Step 1 - Project Structure Setup

**Time Estimate:** 20 minutes

---

### Step 3: Logging Utilities Implementation

**Objective:** Implement utility functions for consistent logging.

**Tasks:**

1. Create the logging_utils.py module:
   ```python
   """
   Logging utilities for the Framework Core Application.
   
   This module provides consistent logging setup and helper functions.
   """
   
   import logging
   import os
   import sys
   from typing import Optional, Dict, Any, Union
   
   def setup_logger(
       name: str,
       level: Union[str, int] = "INFO",
       log_file: Optional[str] = None,
       log_format: Optional[str] = None
   ) -> logging.Logger:
       """
       Create and configure a logger with consistent settings.
       
       Args:
           name: The name of the logger
           level: The logging level (string or integer constant)
           log_file: Optional path to a log file
           log_format: Optional custom log format string
           
       Returns:
           A configured logger instance
       """
       # Convert string level to constant if needed
       if isinstance(level, str):
           level = getattr(logging, level.upper(), logging.INFO)
           
       # Create logger
       logger = logging.getLogger(name)
       logger.setLevel(level)
       
       # Clear existing handlers to avoid duplicates
       if logger.handlers:
           logger.handlers.clear()
       
       # Set default format if not provided
       if not log_format:
           log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
       formatter = logging.Formatter(log_format)
       
       # Add console handler
       console_handler = logging.StreamHandler(sys.stdout)
       console_handler.setFormatter(formatter)
       logger.addHandler(console_handler)
       
       # Add file handler if requested
       if log_file:
           # Ensure directory exists
           log_dir = os.path.dirname(log_file)
           if log_dir and not os.path.exists(log_dir):
               os.makedirs(log_dir, exist_ok=True)
               
           file_handler = logging.FileHandler(log_file)
           file_handler.setFormatter(formatter)
           logger.addHandler(file_handler)
       
       return logger
   
   def get_logger_from_config(config: Dict[str, Any], name: str) -> logging.Logger:
       """
       Create a logger based on configuration settings.
       
       Args:
           config: Configuration dictionary with logging settings
           name: The name for the logger
           
       Returns:
           A configured logger instance
       """
       logging_config = config.get("logging", {})
       level = logging_config.get("level", "INFO")
       log_format = logging_config.get("format")
       log_file = logging_config.get("file")
       
       return setup_logger(name, level, log_file, log_format)
   ```

**Dependencies:** Step 1 - Project Structure Setup

**Time Estimate:** 30 minutes

---

### Step 4: Configuration Manager Implementation

**Objective:** Implement the configuration manager to handle loading, validation, and access to settings.

**Tasks:**

1. Create config_loader.py with the ConfigurationManager class:
   ```python
   """
   Configuration management for the Framework Core Application.
   
   This module handles loading, validation, and access to configuration settings.
   """
   
   import os
   import yaml
   import re
   from typing import Dict, Any, Optional, List
   
   from framework_core.exceptions import ConfigError
   from framework_core.utils.logging_utils import setup_logger
   
   class ConfigurationManager:
       """
       Manages loading, validation, and access to configuration settings.
       """
       
       def __init__(self, config_path: Optional[str] = None, cmd_args: Optional[Dict[str, Any]] = None):
           """
           Initialize the Configuration Manager.
           
           Args:
               config_path: Path to the configuration file (YAML)
               cmd_args: Command-line arguments to override file settings
           """
           self.logger = setup_logger("config_manager")
           self.config_path = config_path or self._find_default_config()
           self.cmd_args = cmd_args or {}
           self.config_data = {}
           
       def load_configuration(self) -> bool:
           """
           Load and validate configuration from file.
           
           Returns:
               True if configuration loaded successfully
               
           Raises:
               ConfigError: If configuration loading or validation fails
           """
           try:
               self._load_from_file()
               self._override_with_cmd_args()
               self._validate_configuration()
               self._expand_environment_variables()
               return True
           except Exception as e:
               raise ConfigError(f"Configuration error: {str(e)}")
               
       def _load_from_file(self) -> None:
           """
           Load configuration from YAML file.
           
           Raises:
               ConfigError: If file cannot be read or parsed
           """
           if not self.config_path:
               self.logger.warning("No configuration file specified, using defaults")
               self.config_data = {}
               return
               
           if not os.path.exists(self.config_path):
               raise ConfigError(f"Configuration file not found: {self.config_path}")
               
           try:
               with open(self.config_path, 'r', encoding='utf-8') as f:
                   self.config_data = yaml.safe_load(f) or {}
                   self.logger.info(f"Loaded configuration from {self.config_path}")
           except Exception as e:
               raise ConfigError(f"Failed to read configuration file: {str(e)}")
               
       def _override_with_cmd_args(self) -> None:
           """
           Override configuration with command-line arguments.
           """
           if not self.cmd_args:
               return
               
           for key, value in self.cmd_args.items():
               # Split nested keys by dot notation (e.g. "logging.level")
               if '.' in key:
                   parts = key.split('.')
                   config = self.config_data
                   for part in parts[:-1]:
                       if part not in config:
                           config[part] = {}
                       config = config[part]
                   config[parts[-1]] = value
               else:
                   self.config_data[key] = value
                   
           self.logger.debug("Applied command-line overrides to configuration")
           
       def _validate_configuration(self) -> None:
           """
           Validate required configuration settings.
           
           Raises:
               ConfigError: If required settings are missing or invalid
           """
           # Check for required top-level keys
           required_keys = ["llm_provider"]
           for key in required_keys:
               if key not in self.config_data:
                   raise ConfigError(f"Required configuration key missing: {key}")
                   
           # Validate LLM provider-specific settings
           llm_provider = self.config_data.get("llm_provider")
           if llm_provider:
               llm_settings = self.config_data.get("llm_settings", {}).get(llm_provider, {})
               if not llm_settings:
                   self.logger.warning(f"No settings found for LLM provider: {llm_provider}")
           
           # Validate paths exist if specified
           if "context_definition_file" in self.config_data:
               context_file = self.config_data["context_definition_file"]
               if context_file and not os.path.exists(context_file):
                   self.logger.warning(f"Context definition file not found: {context_file}")
                   
       def _expand_environment_variables(self) -> None:
           """
           Expand environment variables in configuration values.
           """
           def _process_value(value):
               if isinstance(value, str):
                   # Find ${ENV_VAR} or $ENV_VAR patterns
                   pattern = r'\${([^}]+)}|\$([A-Za-z0-9_]+)'
                   
                   def _replace_env_var(match):
                       env_var = match.group(1) or match.group(2)
                       return os.environ.get(env_var, match.group(0))
                       
                   return re.sub(pattern, _replace_env_var, value)
               elif isinstance(value, dict):
                   return {k: _process_value(v) for k, v in value.items()}
               elif isinstance(value, list):
                   return [_process_value(item) for item in value]
               else:
                   return value
                   
           self.config_data = _process_value(self.config_data)
           self.logger.debug("Expanded environment variables in configuration")
           
       def _find_default_config(self) -> Optional[str]:
           """
           Find the default configuration file path.
           
           Returns:
               Path to the default configuration file, or None if not found
           """
           # Check for environment variable
           if 'FRAMEWORK_CONFIG_PATH' in os.environ:
               return os.environ['FRAMEWORK_CONFIG_PATH']
               
           # Check common locations
           common_paths = [
               "./config.yaml",
               "./config/config.yaml",
               "./framework_config.yaml",
               os.path.expanduser("~/.config/ai_framework/config.yaml")
           ]
           
           for path in common_paths:
               if os.path.exists(path):
                   return path
                   
           return None
           
       def get_llm_provider(self) -> str:
           """
           Get the configured LLM provider.
           
           Returns:
               The LLM provider name
           """
           return self.config_data.get("llm_provider", "gemini_2_5_pro")
           
       def get_context_definition_path(self) -> Optional[str]:
           """
           Get the path to the context definition file.
           
           Returns:
               The context definition file path, or None if not specified
           """
           return self.config_data.get("context_definition_file")
           
       def get_llm_settings(self, provider: Optional[str] = None) -> Dict[str, Any]:
           """
           Get LLM-specific settings.
           
           Args:
               provider: Optional provider name, or use the configured default
               
           Returns:
               Dictionary of LLM-specific settings
           """
           provider = provider or self.get_llm_provider()
           return self.config_data.get("llm_settings", {}).get(provider, {})
           
       def get_teps_settings(self) -> Dict[str, Any]:
           """
           Get TEPS-specific settings.
           
           Returns:
               Dictionary of TEPS-specific settings
           """
           return self.config_data.get("teps_settings", {})
           
       def get_logging_level(self) -> str:
           """
           Get the configured logging level.
           
           Returns:
               The logging level as a string
           """
           return self.config_data.get("logging", {}).get("level", "INFO")
           
       def get_message_history_settings(self) -> Dict[str, Any]:
           """
           Get message history settings.
           
           Returns:
               Dictionary of message history settings
           """
           return self.config_data.get("message_history", {})
           
       def get_all_config(self) -> Dict[str, Any]:
           """
           Get the complete configuration dictionary.
           
           Returns:
               The complete configuration dictionary
           """
           return self.config_data.copy()
   ```

2. Create an example config.yaml file:
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

**Dependencies:** 
- Step 1 - Project Structure Setup
- Step 2 - Exception Hierarchy
- Step 3 - Logging Utilities

**Time Estimate:** 60 minutes

---

### Step 5: Error Handler Implementation

**Objective:** Implement the centralized error handling system.

**Tasks:**

1. Create error_handler.py with the ErrorHandler class:
   ```python
   """
   Centralized error handling and logging for the Framework Core Application.
   
   This module provides a consistent approach to error handling across components.
   """
   
   import logging
   import traceback
   from typing import Optional, Any
   
   from framework_core.utils.logging_utils import setup_logger
   
   class ErrorHandler:
       """
       Provides centralized error handling and logging.
       """
       
       def __init__(self, logger: Optional[logging.Logger] = None):
           """
           Initialize the Error Handler.
           
           Args:
               logger: Optional logger instance
           """
           self.logger = logger or self._setup_default_logger()
           
       def handle_error(
           self, 
           error_type: str, 
           error_message: str, 
           exception: Optional[Exception] = None,
           verbose: bool = False
       ) -> str:
           """
           Handle an error by logging it and returning a formatted error message.
           
           Args:
               error_type: The type of error
               error_message: The error message
               exception: Optional exception object
               verbose: Whether to include additional details in the returned message
               
           Returns:
               Formatted error message for display
           """
           # Log the error
           if exception:
               self.logger.error(f"{error_type}: {error_message}", exc_info=exception)
           else:
               self.logger.error(f"{error_type}: {error_message}")
               
           # Format the message for display
           formatted_message = f"{error_type}: {error_message}"
           
           # Add trace if verbose
           if verbose and exception:
               formatted_message += f"\n\nDetails: {traceback.format_exc()}"
               
           return formatted_message
           
       def _setup_default_logger(self) -> logging.Logger:
           """
           Set up the default logger.
           
           Returns:
               A configured logger instance
           """
           return setup_logger("error_handler")
       
       def get_recovery_instructions(self, error_type: str) -> str:
           """
           Get recovery instructions for a specific error type.
           
           Args:
               error_type: The type of error
               
           Returns:
               Recovery instructions as a string
           """
           recovery_map = {
               "ConfigError": "Check your configuration file for errors or missing values.",
               "ComponentInitError": "Verify component dependencies and try restarting.",
               "DCMInitError": "Check context definition file path and content.",
               "LIALInitError": "Verify LLM API key and provider settings.",
               "TEPSInitError": "Check TEPS settings and permissions.",
               "LLMAPIError": "Check your internet connection and API key validity.",
               "ToolExecutionError": "Verify system permissions and try again.",
               "UserInputError": "Please provide input in the expected format."
           }
           
           return recovery_map.get(error_type, "Please check logs for details and try again.")
   ```

**Dependencies:** 
- Step 1 - Project Structure Setup 
- Step 2 - Exception Hierarchy
- Step 3 - Logging Utilities

**Time Estimate:** 30 minutes

---

### Step 6: Component Manager Implementations

**Objective:** Implement the manager interfaces for DCM, LIAL, and TEPS components.

**Tasks:**

1. Create dcm_manager.py:
   ```python
   """
   DCM (Dynamic Context Manager) integration for the Framework Core Application.
   
   This module provides an interface for interacting with the DCM component.
   """
   
   from typing import Dict, Any, Optional
   import os
   
   from framework_core.exceptions import DCMInitError, ConfigError
   from framework_core.utils.logging_utils import setup_logger
   
   class DCMManager:
       """
       Manages interaction with the Dynamic Context Manager (DCM) component.
       """
       
       def __init__(self, context_definition_path: Optional[str] = None):
           """
           Initialize the DCM Manager.
           
           Args:
               context_definition_path: Path to the context definition file
           """
           self.logger = setup_logger("dcm_manager")
           self.context_definition_path = context_definition_path
           self.dcm_instance = None
           
       def initialize(self) -> bool:
           """
           Initialize the DCM component.
           
           Returns:
               True if initialization succeeded
               
           Raises:
               DCMInitError: If initialization fails
               ConfigError: If required configuration is missing
           """
           if not self.context_definition_path:
               raise ConfigError("Context definition path is required for DCM initialization")
               
           if not os.path.exists(self.context_definition_path):
               raise ConfigError(f"Context definition file not found: {self.context_definition_path}")
               
           try:
               from framework_core.dcm import DynamicContextManager
               self.dcm_instance = DynamicContextManager(self.context_definition_path)
               self.logger.info(f"DCM initialized with context definition: {self.context_definition_path}")
               return True
           except Exception as e:
               raise DCMInitError(f"Failed to initialize DCM: {str(e)}")
               
       def get_initial_prompt(self) -> str:
           """
           Get the initial prompt template from DCM.
           
           Returns:
               The initial prompt template as a string
               
           Raises:
               DCMInitError: If DCM is not initialized
           """
           self._ensure_initialized()
           
           prompt = self.dcm_instance.get_initial_prompt_template()
           if not prompt:
               self.logger.warning("No initial prompt template found in context definition")
               return "Welcome to the AI-Assisted Framework."
               
           return prompt
           
       def get_full_context(self) -> Dict[str, Any]:
           """
           Get the full context loaded by DCM.
           
           Returns:
               Dictionary of all loaded documents
               
           Raises:
               DCMInitError: If DCM is not initialized
           """
           self._ensure_initialized()
           return self.dcm_instance.get_full_initial_context()
           
       def get_document_content(self, doc_id: str) -> Optional[str]:
           """
           Get the content of a specific document from DCM.
           
           Args:
               doc_id: The identifier of the document
               
           Returns:
               Document content as string, or None if not found
               
           Raises:
               DCMInitError: If DCM is not initialized
           """
           self._ensure_initialized()
           return self.dcm_instance.get_document_content(doc_id)
           
       def get_persona_definitions(self) -> Dict[str, str]:
           """
           Get all persona definitions from DCM.
           
           Returns:
               Dictionary mapping persona_id to definition content
               
           Raises:
               DCMInitError: If DCM is not initialized
           """
           self._ensure_initialized()
           return self.dcm_instance.get_persona_definitions()
           
       def _ensure_initialized(self) -> None:
           """
           Ensure the DCM component is initialized.
           
           Raises:
               DCMInitError: If DCM is not initialized
           """
           if not self.dcm_instance:
               raise DCMInitError("DCM is not initialized")
   ```

2. Create lial_manager.py:
   ```python
   """
   LIAL (LLM Interaction Abstraction Layer) integration for the Framework Core Application.
   
   This module provides an interface for interacting with the LIAL component.
   """
   
   from typing import Dict, List, Any, Optional
   
   from framework_core.exceptions import LIALInitError, ConfigError
   from framework_core.utils.logging_utils import setup_logger
   
   class LIALManager:
       """
       Manages interaction with the LLM Interaction Abstraction Layer (LIAL) component.
       """
       
       def __init__(
           self, 
           llm_provider: str, 
           llm_settings: Dict[str, Any], 
           dcm_manager: 'DCMManager'
       ):
           """
           Initialize the LIAL Manager.
           
           Args:
               llm_provider: The LLM provider to use
               llm_settings: Provider-specific settings
               dcm_manager: The DCM manager instance
           """
           self.logger = setup_logger("lial_manager")
           self.llm_provider = llm_provider
           self.llm_settings = llm_settings
           self.dcm_manager = dcm_manager
           self.adapter_instance = None
           
       def initialize(self) -> bool:
           """
           Initialize the LIAL adapter.
           
           Returns:
               True if initialization succeeded
               
           Raises:
               LIALInitError: If initialization fails
               ConfigError: If required configuration is missing
           """
           if not self.llm_provider:
               raise ConfigError("LLM provider is required for LIAL initialization")
               
           try:
               adapter_class = self._get_adapter_class()
               self.adapter_instance = adapter_class(
                   config=self.llm_settings,
                   dcm_instance=self.dcm_manager.dcm_instance
               )
               self.logger.info(f"LIAL initialized with provider: {self.llm_provider}")
               return True
           except Exception as e:
               raise LIALInitError(f"Failed to initialize LIAL: {str(e)}")
               
       def _get_adapter_class(self):
           """
           Get the appropriate adapter class based on the provider.
           
           Returns:
               Adapter class for the configured provider
               
           Raises:
               LIALInitError: If adapter not found for provider
           """
           if self.llm_provider == "gemini_2_5_pro":
               try:
                   from framework_core.adapters.gemini_adapter import GeminiAdapter
                   return GeminiAdapter
               except ImportError as e:
                   raise LIALInitError(f"Failed to import GeminiAdapter: {str(e)}")
           else:
               raise LIALInitError(f"Unsupported LLM provider: {self.llm_provider}")
               
       def send_messages(
           self, 
           messages: List[Dict[str, Any]], 
           active_persona_id: Optional[str] = None
       ) -> Dict[str, Any]:
           """
           Send messages to the LLM via the LIAL adapter.
           
           Args:
               messages: List of messages to send
               active_persona_id: Optional ID of the active persona
               
           Returns:
               LLMResponse object with conversation and optional tool request
               
           Raises:
               LIALInitError: If LIAL is not initialized
           """
           self._ensure_initialized()
           
           try:
               return self.adapter_instance.send_message_sequence(messages, active_persona_id)
           except Exception as e:
               self.logger.error(f"Error sending messages: {str(e)}")
               return {
                   "conversation": f"Error communicating with LLM: {str(e)}",
                   "tool_request": None
               }
               
       def _ensure_initialized(self) -> None:
           """
           Ensure the LIAL component is initialized.
           
           Raises:
               LIALInitError: If LIAL is not initialized
           """
           if not self.adapter_instance:
               raise LIALInitError("LIAL is not initialized")
   ```

3. Create teps_manager.py:
   ```python
   """
   TEPS (Tool Execution & Permission Service) integration for the Framework Core Application.
   
   This module provides an interface for interacting with the TEPS component.
   """
   
   from typing import Dict, Any, Optional
   
   from framework_core.exceptions import TEPSInitError, ConfigError
   from framework_core.utils.logging_utils import setup_logger
   
   class TEPSManager:
       """
       Manages interaction with the Tool Execution & Permission Service (TEPS) component.
       """
       
       def __init__(self, teps_settings: Optional[Dict[str, Any]] = None):
           """
           Initialize the TEPS Manager.
           
           Args:
               teps_settings: Configuration settings for TEPS
           """
           self.logger = setup_logger("teps_manager")
           self.teps_settings = teps_settings or {}
           self.teps_instance = None
           
       def initialize(self) -> bool:
           """
           Initialize the TEPS component.
           
           Returns:
               True if initialization succeeded
               
           Raises:
               TEPSInitError: If initialization fails
           """
           try:
               from framework_core.teps import TEPSEngine
               self.teps_instance = TEPSEngine(config=self.teps_settings)
               self.logger.info("TEPS initialized successfully")
               return True
           except Exception as e:
               raise TEPSInitError(f"Failed to initialize TEPS: {str(e)}")
               
       def execute_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
           """
           Execute a tool via TEPS.
           
           Args:
               tool_request: The tool request to execute
               
           Returns:
               ToolResult object with the result of the tool execution
               
           Raises:
               TEPSInitError: If TEPS is not initialized
           """
           self._ensure_initialized()
           
           try:
               self.logger.info(f"Executing tool: {tool_request.get('tool_name', 'unknown')}")
               return self.teps_instance.execute_tool(tool_request)
           except Exception as e:
               self.logger.error(f"Error executing tool: {str(e)}")
               return {
                   "request_id": tool_request.get("request_id", "unknown_request"),
                   "tool_name": tool_request.get("tool_name", "unknown_tool"),
                   "status": "error",
                   "data": {
                       "error_message": str(e)
                   }
               }
               
       def _ensure_initialized(self) -> None:
           """
           Ensure the TEPS component is initialized.
           
           Raises:
               TEPSInitError: If TEPS is not initialized
           """
           if not self.teps_instance:
               raise TEPSInitError("TEPS is not initialized")
   ```

**Dependencies:** 
- Step 1 - Project Structure Setup
- Step 2 - Exception Hierarchy
- Step 3 - Logging Utilities
- Step 4 - Configuration Manager

**Time Estimate:** 90 minutes

---

### Step 7: Framework Controller (Basic Implementation)

**Objective:** Implement the core Framework Controller class with initialization capability.

**Tasks:**

1. Create controller.py with the FrameworkController class:
   ```python
   """
   Central controller for the Framework Core Application.
   
   This module implements the Framework Controller, which orchestrates
   the initialization and operation of all components.
   """
   
   from typing import Optional, Dict, Any
   
   from framework_core.exceptions import (
       ConfigError, 
       DCMInitError, 
       LIALInitError, 
       TEPSInitError,
       ComponentInitError
   )
   from framework_core.component_managers.dcm_manager import DCMManager
   from framework_core.component_managers.lial_manager import LIALManager
   from framework_core.component_managers.teps_manager import TEPSManager
   from framework_core.error_handler import ErrorHandler
   from framework_core.utils.logging_utils import setup_logger
   
   class FrameworkController:
       """
       Central orchestrator of the Framework Core Application.
       Manages component initialization, interaction flow, and lifecycle.
       """
       
       def __init__(self, config_manager: 'ConfigurationManager'):
           """
           Initialize the Framework Controller with configuration.
           
           Args:
               config_manager: Configuration manager instance
           """
           self.logger = setup_logger("framework_controller")
           self.config_manager = config_manager
           self.dcm_manager = None
           self.lial_manager = None
           self.teps_manager = None
           self.message_manager = None
           self.ui_manager = None
           self.tool_request_handler = None
           self.error_handler = ErrorHandler()
           self.running = False
           
       def initialize(self) -> bool:
           """
           Initialize all framework components.
           
           Returns:
               True if initialization succeeded, False otherwise
           """
           try:
               self.logger.info("Starting Framework Core Application initialization")
               
               # Initialize components in dependency order
               success = self._initialize_dcm()
               if not success:
                   return False
                   
               success = self._initialize_lial()
               if not success:
                   return False
                   
               success = self._initialize_teps()
               if not success:
                   return False
                   
               # Initialize supporting components (minimal stubs for Phase 1)
               self.message_manager = self._stub_message_manager()
               self.ui_manager = self._stub_ui_manager()
               self.tool_request_handler = self._stub_tool_request_handler()
               
               self.logger.info("Framework Core Application initialized successfully")
               return True
               
           except Exception as e:
               error_message = self.error_handler.handle_error(
                   "Initialization Error", 
                   str(e), 
                   exception=e
               )
               self.logger.error(f"Initialization failed: {error_message}")
               return False
           
       def _initialize_dcm(self) -> bool:
           """
           Initialize the DCM component.
           
           Returns:
               True if initialization succeeded, False otherwise
           """
           try:
               context_definition_path = self.config_manager.get_context_definition_path()
               self.logger.info(f"Initializing DCM with context definition: {context_definition_path}")
               
               self.dcm_manager = DCMManager(context_definition_path)
               self.dcm_manager.initialize()
               
               self.logger.info("DCM initialization successful")
               return True
               
           except (DCMInitError, ConfigError) as e:
               self.error_handler.handle_error(
                   "DCM Initialization Error", 
                   str(e), 
                   exception=e
               )
               return False
           
       def _initialize_lial(self) -> bool:
           """
           Initialize the LIAL component with the appropriate adapter.
           
           Returns:
               True if initialization succeeded, False otherwise
           """
           try:
               if not self.dcm_manager:
                   raise ComponentInitError("Cannot initialize LIAL: DCM not initialized")
                   
               llm_provider = self.config_manager.get_llm_provider()
               llm_settings = self.config_manager.get_llm_settings()
               
               self.logger.info(f"Initializing LIAL with provider: {llm_provider}")
               
               self.lial_manager = LIALManager(
                   llm_provider=llm_provider,
                   llm_settings=llm_settings,
                   dcm_manager=self.dcm_manager
               )
               self.lial_manager.initialize()
               
               self.logger.info("LIAL initialization successful")
               return True
               
           except (LIALInitError, ConfigError, ComponentInitError) as e:
               self.error_handler.handle_error(
                   "LIAL Initialization Error", 
                   str(e), 
                   exception=e
               )
               return False
           
       def _initialize_teps(self) -> bool:
           """
           Initialize the TEPS component.
           
           Returns:
               True if initialization succeeded, False otherwise
           """
           try:
               teps_settings = self.config_manager.get_teps_settings()
               
               self.logger.info("Initializing TEPS")
               
               self.teps_manager = TEPSManager(teps_settings)
               self.teps_manager.initialize()
               
               self.logger.info("TEPS initialization successful")
               return True
               
           except (TEPSInitError, ConfigError) as e:
               self.error_handler.handle_error(
                   "TEPS Initialization Error", 
                   str(e), 
                   exception=e
               )
               return False
               
       def _stub_message_manager(self) -> Dict[str, Any]:
           """
           Create a simple stub for the message manager (Phase 1 placeholder).
           
           Returns:
               A simple dict with message storage capability
           """
           self.logger.info("Creating message manager stub")
           return {
               "messages": [],
               "add_message": lambda msg: None  # Placeholder
           }
           
       def _stub_ui_manager(self) -> Dict[str, Any]:
           """
           Create a simple stub for the UI manager (Phase 1 placeholder).
           
           Returns:
               A simple dict with basic UI capabilities
           """
           self.logger.info("Creating UI manager stub")
           return {
               "display_message": lambda msg: print(f"[SYSTEM]: {msg}")
           }
           
       def _stub_tool_request_handler(self) -> Dict[str, Any]:
           """
           Create a simple stub for the tool request handler (Phase 1 placeholder).
           
           Returns:
               A simple dict with tool handling capability
           """
           self.logger.info("Creating tool request handler stub")
           return {
               "handle_tool_request": lambda req: None  # Placeholder
           }
           
       def shutdown(self) -> None:
           """
           Perform graceful shutdown of the framework.
           """
           self.logger.info("Framework shutdown initiated")
           self.running = False
           # Future: Add cleanup for each component if needed
   ```

**Dependencies:** 
- Step 1 - Project Structure Setup
- Step 2 - Exception Hierarchy
- Step 3 - Logging Utilities
- Step 4 - Configuration Manager
- Step 5 - Error Handler
- Step 6 - Component Managers

**Time Estimate:** 60 minutes

---

### Step 8: Main Entry Point Implementation

**Objective:** Create the main entry point script that initializes and launches the Framework Controller.

**Tasks:**

1. Create run_framework.py:
   ```python
   #!/usr/bin/env python3
   """
   Main entry point for the Framework Core Application.
   
   This script initializes the framework components and starts the application.
   """
   
   import os
   import sys
   import argparse
   from typing import Dict, Any
   
   # Add parent directory to path if needed
   sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
   
   from framework_core.config_loader import ConfigurationManager
   from framework_core.controller import FrameworkController
   from framework_core.utils.logging_utils import setup_logger
   
   def parse_arguments() -> Dict[str, Any]:
       """
       Parse command-line arguments.
       
       Returns:
           Dictionary of parsed arguments
       """
       parser = argparse.ArgumentParser(description="Framework Core Application")
       
       parser.add_argument(
           "--config", 
           "-c", 
           dest="config_path",
           help="Path to configuration file"
       )
       
       parser.add_argument(
           "--log-level", 
           "-l", 
           dest="logging.level",
           choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
           help="Logging level"
       )
       
       parser.add_argument(
           "--llm-provider", 
           dest="llm_provider",
           help="LLM provider to use"
       )
       
       parser.add_argument(
           "--context-file", 
           dest="context_definition_file",
           help="Path to context definition file"
       )
       
       # Parse args and convert to dict
       args = parser.parse_args()
       config_path = args.config_path
       
       # Remove config_path and convert the rest to a dict
       args_dict = {k: v for k, v in vars(args).items() if k != "config_path" and v is not None}
       
       return config_path, args_dict
   
   def main() -> int:
       """
       Main entry point function.
       
       Returns:
           Exit code (0 for success, non-zero for failure)
       """
       logger = setup_logger("main")
       logger.info("Starting Framework Core Application")
       
       try:
           # Parse command-line arguments
           config_path, cmd_args = parse_arguments()
           
           # Initialize configuration
           config_manager = ConfigurationManager(config_path, cmd_args)
           if not config_manager.load_configuration():
               logger.error("Failed to load configuration")
               return 1
               
           # Initialize framework controller
           controller = FrameworkController(config_manager)
           if not controller.initialize():
               logger.error("Failed to initialize framework controller")
               return 1
               
           # Print success message (in Phase 1, we just initialize and exit)
           print("\nFramework Core Application initialized successfully!")
           print("Phase 1 implementation complete - initialization only.")
           print("(Future phases will implement the main interaction loop)")
           
           return 0
           
       except KeyboardInterrupt:
           logger.info("Framework terminated by user")
           return 0
           
       except Exception as e:
           logger.exception(f"Unhandled exception: {str(e)}")
           return 1
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

2. Add executable permission to the script:
   ```bash
   chmod +x run_framework.py
   ```

**Dependencies:** All previous steps

**Time Estimate:** 30 minutes

---

### Step 9: Unit Testing

**Objective:** Create comprehensive unit tests for the implemented components.

**Tasks:**

1. Set up the tests directory structure:
   ```
   tests/
   ├── __init__.py
   ├── unit/
   │   ├── __init__.py
   │   ├── test_config_loader.py
   │   ├── test_controller.py
   │   ├── test_error_handler.py
   │   ├── component_managers/
   │   │   ├── __init__.py
   │   │   ├── test_dcm_manager.py
   │   │   ├── test_lial_manager.py
   │   │   └── test_teps_manager.py
   │   └── utils/
   │       ├── __init__.py
   │       └── test_logging_utils.py
   └── integration/
       ├── __init__.py
       └── test_initialization.py
   ```

2. Implement a sample unit test for ConfigurationManager (tests/unit/test_config_loader.py):
   ```python
   """
   Unit tests for the Configuration Manager.
   """
   
   import os
   import tempfile
   import unittest
   from unittest.mock import patch, MagicMock
   
   from framework_core.config_loader import ConfigurationManager
   from framework_core.exceptions import ConfigError
   
   class TestConfigurationManager(unittest.TestCase):
       """Test cases for ConfigurationManager."""
       
       def setUp(self):
           """Set up test fixtures."""
           # Create a temporary config file
           self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
           self.temp_file.write(b"""
   llm_provider: "test_provider"
   context_definition_file: "./test_context.md"
   
   llm_settings:
     test_provider:
       model_name: "test-model"
       temperature: 0.5
   
   teps_settings:
     allowlist_file: ".test_allowlist.json"
   
   logging:
     level: "INFO"
   """)
           self.temp_file.close()
           
       def tearDown(self):
           """Tear down test fixtures."""
           os.unlink(self.temp_file.name)
           
       def test_load_configuration_from_file(self):
           """Test loading configuration from a file."""
           config_manager = ConfigurationManager(self.temp_file.name)
           config_manager.load_configuration()
           
           # Test that values were loaded correctly
           self.assertEqual(config_manager.get_llm_provider(), "test_provider")
           self.assertEqual(config_manager.get_context_definition_path(), "./test_context.md")
           self.assertEqual(config_manager.get_logging_level(), "INFO")
           
           # Test LLM settings
           llm_settings = config_manager.get_llm_settings()
           self.assertEqual(llm_settings.get("model_name"), "test-model")
           self.assertEqual(llm_settings.get("temperature"), 0.5)
           
       def test_override_with_cmd_args(self):
           """Test overriding config with command-line arguments."""
           cmd_args = {
               "llm_provider": "override_provider",
               "logging.level": "DEBUG"
           }
           
           config_manager = ConfigurationManager(self.temp_file.name, cmd_args)
           config_manager.load_configuration()
           
           # Test that values were overridden
           self.assertEqual(config_manager.get_llm_provider(), "override_provider")
           self.assertEqual(config_manager.get_logging_level(), "DEBUG")
           
       def test_missing_config_file(self):
           """Test behavior with a missing config file."""
           config_manager = ConfigurationManager("non_existent_file.yaml")
           
           # Should raise ConfigError
           with self.assertRaises(ConfigError):
               config_manager.load_configuration()
               
       def test_expand_environment_variables(self):
           """Test environment variable expansion in config values."""
           # Create a temporary file with env vars
           env_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
           env_temp_file.write(b"""
   api_key: "${TEST_API_KEY}"
   context_path: "$TEST_PATH/context"
   """)
           env_temp_file.close()
           
           # Mock environment variables
           with patch.dict(os.environ, {
               "TEST_API_KEY": "test_key_123",
               "TEST_PATH": "/test/path"
           }):
               config_manager = ConfigurationManager(env_temp_file.name)
               config_manager.load_configuration()
               
               config = config_manager.get_all_config()
               self.assertEqual(config.get("api_key"), "test_key_123")
               self.assertEqual(config.get("context_path"), "/test/path/context")
               
           # Clean up
           os.unlink(env_temp_file.name)
   
   if __name__ == '__main__':
       unittest.main()
   ```

3. Implement Integration Test for Initialization (tests/integration/test_initialization.py):
   ```python
   """
   Integration tests for the Framework Core Application initialization.
   """
   
   import os
   import tempfile
   import unittest
   from unittest.mock import patch, MagicMock
   
   from framework_core.config_loader import ConfigurationManager
   from framework_core.controller import FrameworkController
   
   class TestFrameworkInitialization(unittest.TestCase):
       """Test cases for end-to-end initialization."""
       
       def setUp(self):
           """Set up test fixtures."""
           # Create a temporary config file
           self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
           self.temp_file.write(b"""
   llm_provider: "gemini_2_5_pro"
   context_definition_file: "./test_context.md"
   
   llm_settings:
     gemini_2_5_pro:
       model_name: "test-model"
       temperature: 0.5
   
   teps_settings:
     allowlist_file: ".test_allowlist.json"
   
   logging:
     level: "INFO"
   """)
           self.temp_file.close()
           
       def tearDown(self):
           """Tear down test fixtures."""
           os.unlink(self.temp_file.name)
           
       @patch('framework_core.component_managers.dcm_manager.DCMManager')
       @patch('framework_core.component_managers.lial_manager.LIALManager')
       @patch('framework_core.component_managers.teps_manager.TEPSManager')
       def test_framework_initialization(self, mock_teps, mock_lial, mock_dcm):
           """Test the complete initialization sequence."""
           # Mock DCM manager
           mock_dcm_instance = MagicMock()
           mock_dcm.return_value = mock_dcm_instance
           mock_dcm_instance.initialize.return_value = True
           
           # Mock LIAL manager
           mock_lial_instance = MagicMock()
           mock_lial.return_value = mock_lial_instance
           mock_lial_instance.initialize.return_value = True
           
           # Mock TEPS manager
           mock_teps_instance = MagicMock()
           mock_teps.return_value = mock_teps_instance
           mock_teps_instance.initialize.return_value = True
           
           # Initialize the configuration
           config_manager = ConfigurationManager(self.temp_file.name)
           config_manager.load_configuration()
           
           # Initialize the controller
           controller = FrameworkController(config_manager)
           result = controller.initialize()
           
           # Verify initialization succeeded
           self.assertTrue(result)
           
           # Verify each component was initialized
           mock_dcm_instance.initialize.assert_called_once()
           mock_lial_instance.initialize.assert_called_once()
           mock_teps_instance.initialize.assert_called_once()
           
       @patch('framework_core.component_managers.dcm_manager.DCMManager')
       def test_framework_initialization_dcm_failure(self, mock_dcm):
           """Test initialization with DCM failure."""
           # Mock DCM manager to fail
           mock_dcm_instance = MagicMock()
           mock_dcm.return_value = mock_dcm_instance
           mock_dcm_instance.initialize.side_effect = Exception("DCM init failed")
           
           # Initialize the configuration
           config_manager = ConfigurationManager(self.temp_file.name)
           config_manager.load_configuration()
           
           # Initialize the controller
           controller = FrameworkController(config_manager)
           result = controller.initialize()
           
           # Verify initialization failed
           self.assertFalse(result)
   
   if __name__ == '__main__':
       unittest.main()
   ```

**Dependencies:** All previous implementation steps

**Time Estimate:** 120 minutes (basic tests; more would be needed for complete coverage)

---

### Step 10: Example Configuration and Documentation

**Objective:** Create example configuration files and documentation to facilitate usage.

**Tasks:**

1. Create a sample configuration file (config/config.yaml):
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
       system_instruction_id: "system_prompt"  # Optional ID of system instruction in context
   
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
   
   # Message History Settings (for future phases)
   message_history:
     max_length: 100
     prioritize_system_messages: true
     pruning_strategy: "remove_oldest"  # remove_oldest, summarize
   
   # User Interface Settings (for future phases)
   ui:
     input_prompt: "> "
     assistant_prefix: "(AI): "
     system_prefix: "[System]: "
     error_prefix: "[Error]: "
   ```

2. Create a sample context definition file (config/FRAMEWORK_CONTEXT.md.example):
   ```markdown
   # Framework Context Definition

   # initial_prompt_template: "Welcome to the AI-Assisted Framework. I'm here to help you with your task. How can I assist you today?"

   ## Personas
   catalyst_persona: @personas/catalyst_persona.md
   forge_persona: @personas/forge_persona.md

   ## Standards
   ai_dev_bible: @standards/ai_assisted_dev_bible.md

   ## Workflows
   maia_workflow: @workflows/maia_workflow.md

   ## System Instructions
   system_prompt: @system/main_prompt.md
   ```

3. Create a README.md for the Framework Core Application:
   ```markdown
   # Framework Core Application

   The Framework Core Application is the central orchestrator for the AI-Assisted Framework V2, integrating the LIAL (LLM Interaction Abstraction Layer), TEPS (Tool Execution & Permission Service), and DCM (Dynamic Context Manager) components.

   ## Phase 1 Implementation

   Phase 1 focuses on establishing the basic skeleton, component interfaces, configuration management, and the initialization sequence that enables the framework to start up and properly integrate the existing components.

   ### Current Status

   - ✅ Project structure setup
   - ✅ Configuration management
   - ✅ Error handling
   - ✅ Component integration interfaces
   - ✅ Basic framework controller (initialization only)
   - ✅ Unit testing

   ## Usage

   ### Prerequisites

   - Python 3.9+
   - PyYAML
   - Access to the Gemini API (or other supported LLM)

   ### Configuration

   1. Copy `config/config.yaml.example` to `config/config.yaml`
   2. Copy `config/FRAMEWORK_CONTEXT.md.example` to `config/FRAMEWORK_CONTEXT.md`
   3. Set up environment variables:
      ```bash
      export GEMINI_API_KEY="your-api-key"
      ```

   ### Running the Framework

   ```bash
   # Basic usage
   python run_framework.py

   # With custom config
   python run_framework.py --config /path/to/config.yaml

   # With command-line overrides
   python run_framework.py --log-level DEBUG --llm-provider gemini_2_5_pro
   ```

   ## Component Architecture

   The Framework Core Application consists of the following main components:

   1. **Framework Controller**: The central orchestrator that manages the interaction flow and component lifecycle.
   2. **Configuration Manager**: Handles loading, validation, and access to configuration settings.
   3. **Component Managers**: Abstract interfaces for interacting with LIAL, TEPS, and DCM.
   4. **Error Handler**: Centralized error handling and logging.

   ## Next Steps (Future Phases)

   - Message Manager implementation
   - Tool Request Handler implementation
   - User Interface Manager implementation
   - Main interaction loop implementation
   ```

**Dependencies:** All previous steps

**Time Estimate:** 30 minutes

---

## 3. Timeline

Based on the implementation steps outlined above, here's an estimated timeline for Phase 1 implementation:

1. Project Structure Setup: 30 minutes
2. Exception Hierarchy Implementation: 20 minutes
3. Logging Utilities Implementation: 30 minutes
4. Configuration Manager Implementation: 60 minutes
5. Error Handler Implementation: 30 minutes
6. Component Manager Implementations: 90 minutes
7. Framework Controller (Basic Implementation): 60 minutes
8. Main Entry Point Implementation: 30 minutes
9. Unit Testing: 120 minutes
10. Example Configuration and Documentation: 30 minutes

**Total Estimated Time:** 500 minutes (approximately 8.3 hours)

This estimate assumes that the developer is familiar with Python and the existing components. Actual implementation time may vary based on experience level and unforeseen technical challenges.

## 4. Testing Strategy

1. **Unit Testing:**
   - Each component should have its own test suite
   - Mock dependencies to isolate component behavior
   - Focus on testing error handling and edge cases
   - Aim for >85% code coverage

2. **Integration Testing:**
   - Test the entire initialization sequence end-to-end
   - Verify component interactions work correctly
   - Test failure scenarios to ensure graceful degradation

3. **Manual Testing:**
   - Verify the configuration file parsing
   - Test command-line arguments
   - Confirm error messages are clear and helpful

## 5. Conclusion

This implementation plan provides a comprehensive guide for implementing Phase 1 of the Framework Core Application. By following the steps outlined above, Forge should be able to create a solid foundation for the application that successfully initializes and integrates the LIAL, TEPS, and DCM components.

The implementation focuses on establishing a clean architecture with clear separation of concerns, robust error handling, and comprehensive testing. Future phases will build upon this foundation to implement the complete functionality of the Framework Core Application.