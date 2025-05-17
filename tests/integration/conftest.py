"""
Pytest configuration and fixtures for integration tests.

This module provides pytest fixtures and configuration for integration testing the
KeystoneAI-Framework, including:
- Common test configuration
- Shared fixtures for test components
- Mock setup for external dependencies
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.exceptions import (
    ConfigError, 
    DCMInitError, 
    LIALInitError, 
    TEPSInitError,
    ComponentInitError,
    ToolExecutionError
)
from framework_core.lial_core import Message, LLMResponse, ToolRequest, ToolResult

from tests.integration.utils import MockLLMAdapter, ResponseBuilder, MockIOCapture


# Configuration fixtures

@pytest.fixture
def mock_minimal_config():
    """Provide a minimal valid configuration."""
    return {
        "llm_provider": "mock",
        "context_definition_file": "/path/to/FRAMEWORK_CONTEXT.md",
    }


@pytest.fixture
def mock_complete_config():
    """Provide a complete configuration with all settings."""
    return {
        "llm_provider": "mock",
        "context_definition_file": "/path/to/FRAMEWORK_CONTEXT.md",
        "default_persona": "forge",
        "llm_settings": {
            "model_name": "mock-llm",
            "temperature": 0.7,
            "max_tokens": 1000,
            "api_key_env_var": "MOCK_API_KEY",
            "system_instruction_id": "main_system_prompt"
        },
        "teps_settings": {
            "bash": {
                "allowed_commands": ["ls", "echo", "cat"],
                "max_execution_time": 30
            },
            "dry_run_enabled": True
        },
        "ui_settings": {
            "prompt_prefix": "> ",
            "output_formatting": "colorized"
        },
        "message_history_settings": {
            "max_length": 100,
            "pruning_strategy": "remove_oldest",
            "prioritize_system_messages": True
        }
    }


@pytest.fixture
def mock_io_capture():
    """Provide a MockIOCapture instance for testing UI interactions."""
    io_capture = MockIOCapture()
    io_capture.start_capture()
    io_capture.patch_input()
    
    yield io_capture
    
    io_capture.reset()


# Component fixtures

@pytest.fixture
def mock_dcm_instance():
    """Provide a mock DCM instance."""
    mock_dcm = MagicMock(name="DynamicContextManager")
    
    # Configure common methods
    mock_dcm.get_document_content.side_effect = lambda doc_id: (
        "Base system instruction text" if doc_id == "main_system_prompt" 
        else ("# Catalyst Persona\nThe strategic AI planner." if doc_id == "persona_catalyst"
              else ("# Forge Persona\nThe expert AI implementer." if doc_id == "persona_forge"
                    else None))
    )
    
    mock_dcm.get_initial_prompt_template.return_value = (
        "You are an AI assistant in the KeystoneAI-Framework. "
        "You can help users with a variety of tasks."
    )
    
    mock_dcm.get_full_initial_context.return_value = {
        "main_system_prompt": "Base system instruction text",
        "persona_catalyst": "# Catalyst Persona\nThe strategic AI planner.",
        "persona_forge": "# Forge Persona\nThe expert AI implementer."
    }
    
    mock_dcm.get_persona_definitions.return_value = {
        "catalyst": "# Catalyst Persona\nThe strategic AI planner.",
        "forge": "# Forge Persona\nThe expert AI implementer."
    }
    
    return mock_dcm


@pytest.fixture
def mock_dcm_manager(mock_dcm_instance):
    """Provide a mock DCMManager instance."""
    mock_manager = MagicMock(name="DCMManager")
    mock_manager.dcm_instance = mock_dcm_instance
    
    # Configure manager methods to delegate to dcm_instance
    mock_manager.get_initial_prompt.return_value = mock_dcm_instance.get_initial_prompt_template()
    mock_manager.get_full_context.return_value = mock_dcm_instance.get_full_initial_context()
    mock_manager.get_document_content.side_effect = mock_dcm_instance.get_document_content
    mock_manager.get_persona_definitions.return_value = mock_dcm_instance.get_persona_definitions()
    
    return mock_manager


@pytest.fixture
def mock_llm_adapter():
    """Provide a mock LLM adapter instance."""
    adapter = MockLLMAdapter(
        config={
            "model_name": "mock-llm",
            "temperature": 0.7,
            "api_key_env_var": "MOCK_API_KEY"
        },
        dcm_instance=MagicMock()
    )
    
    # Configure common responses
    adapter.configure_response("default", {
        "conversation": "I am an AI assistant. How can I help you today?",
        "tool_request": None
    })
    
    adapter.configure_response("read_file", ResponseBuilder.tool_request(
        tool_name="readFile",
        parameters={"file_path": "/path/to/file.txt"},
        conversation_text="I'll read that file for you.",
        request_id="read-123"
    ))
    
    adapter.configure_response("write_file", ResponseBuilder.tool_request(
        tool_name="writeFile",
        parameters={"file_path": "/path/to/file.txt", "content": "New content"},
        conversation_text="I'll write to that file for you.",
        request_id="write-456"
    ))
    
    adapter.configure_response("bash", ResponseBuilder.tool_request(
        tool_name="executeBashCommand",
        parameters={"command": "ls -la"},
        conversation_text="I'll run that command for you.",
        request_id="bash-789"
    ))
    
    # Configure patterns
    adapter.configure_pattern("read file", "read_file")
    adapter.configure_pattern("write file", "write_file")
    adapter.configure_pattern("run command", "bash")
    
    return adapter


@pytest.fixture
def mock_lial_manager(mock_llm_adapter):
    """Provide a mock LIALManager instance."""
    mock_manager = MagicMock(name="LIALManager")
    
    # Configure the send_messages method to delegate to the adapter
    mock_manager.send_messages.side_effect = mock_llm_adapter.send_message_sequence
    
    return mock_manager


@pytest.fixture
def mock_teps_instance():
    """Provide a mock TEPS instance."""
    mock_teps = MagicMock(name="TEPSEngine")
    
    # Configure execute_tool method with common behavior
    def mock_execute_tool(tool_request):
        tool_name = tool_request.get("tool_name", "unknown")
        request_id = tool_request.get("request_id", "unknown")
        
        if tool_name == "readFile":
            return {
                "request_id": request_id,
                "tool_name": tool_name,
                "status": "success",
                "data": "Content of the requested file."
            }
        elif tool_name == "writeFile":
            return {
                "request_id": request_id,
                "tool_name": tool_name,
                "status": "success",
                "data": {"bytes_written": 123, "path": tool_request.get("parameters", {}).get("file_path")}
            }
        elif tool_name == "executeBashCommand":
            return {
                "request_id": request_id,
                "tool_name": tool_name,
                "status": "success",
                "data": "Command output here"
            }
        elif "error" in tool_name.lower():
            return {
                "request_id": request_id,
                "tool_name": tool_name,
                "status": "error",
                "data": {"error_message": "Tool execution failed"}
            }
        else:
            return {
                "request_id": request_id,
                "tool_name": tool_name,
                "status": "success",
                "data": {"message": "Tool executed successfully"}
            }
    
    mock_teps.execute_tool.side_effect = mock_execute_tool
    
    return mock_teps


@pytest.fixture
def mock_teps_manager(mock_teps_instance):
    """Provide a mock TEPSManager instance."""
    mock_manager = MagicMock(name="TEPSManager")
    mock_manager.teps_instance = mock_teps_instance
    
    # Configure manager's execute_tool to delegate to teps_instance
    mock_manager.execute_tool.side_effect = mock_teps_instance.execute_tool
    
    return mock_manager


@pytest.fixture
def mock_message_manager():
    """Provide a mock MessageManager instance."""
    mock_manager = MagicMock(name="MessageManager")
    
    # Initialize with empty message list
    mock_manager.messages = []
    
    # Track added messages for verification
    mock_manager.added_messages = {
        "system": [],
        "user": [],
        "assistant": [],
        "tool_result": []
    }
    
    # Configure add_*_message methods to update both messages list and tracking dict
    def add_system_message(content):
        message = {"role": "system", "content": content}
        mock_manager.messages.append(message)
        mock_manager.added_messages["system"].append(message)
    
    def add_user_message(content):
        message = {"role": "user", "content": content}
        mock_manager.messages.append(message)
        mock_manager.added_messages["user"].append(message)
    
    def add_assistant_message(content):
        message = {"role": "assistant", "content": content}
        mock_manager.messages.append(message)
        mock_manager.added_messages["assistant"].append(message)
    
    def add_tool_result_message(tool_name, content, tool_call_id):
        message = {
            "role": "tool_result",
            "content": content,
            "tool_name": tool_name,
            "tool_call_id": tool_call_id
        }
        mock_manager.messages.append(message)
        mock_manager.added_messages["tool_result"].append(message)
    
    mock_manager.add_system_message.side_effect = add_system_message
    mock_manager.add_user_message.side_effect = add_user_message
    mock_manager.add_assistant_message.side_effect = add_assistant_message
    mock_manager.add_tool_result_message.side_effect = add_tool_result_message
    
    # Configure get_messages to return a formatted copy
    def get_messages(include_roles=None, exclude_roles=None, for_llm=False):
        messages = mock_manager.messages.copy()
        
        if include_roles:
            messages = [m for m in messages if m.get("role") in include_roles]
        
        if exclude_roles:
            messages = [m for m in messages if m.get("role") not in exclude_roles]
        
        if for_llm:
            # Transform tool_result messages for LLM format
            formatted = []
            for msg in messages:
                if msg.get("role") == "tool_result":
                    formatted.append({
                        "role": "tool",
                        "content": msg.get("content"),
                        "name": msg.get("tool_name"),
                        "tool_call_id": msg.get("tool_call_id")
                    })
                else:
                    # Copy standard messages
                    formatted.append({
                        "role": msg.get("role"),
                        "content": msg.get("content")
                    })
            return formatted
        
        return messages
    
    mock_manager.get_messages.side_effect = get_messages
    
    # Configure clear_history
    def clear_history(preserve_system=True):
        if preserve_system:
            mock_manager.messages = [m for m in mock_manager.messages if m.get("role") == "system"]
            mock_manager.added_messages["user"] = []
            mock_manager.added_messages["assistant"] = []
            mock_manager.added_messages["tool_result"] = []
        else:
            mock_manager.messages = []
            for key in mock_manager.added_messages:
                mock_manager.added_messages[key] = []
    
    mock_manager.clear_history.side_effect = clear_history
    
    return mock_manager


@pytest.fixture
def mock_ui_manager(mock_io_capture):
    """Provide a mock UIManager instance."""
    mock_manager = MagicMock(name="UserInterfaceManager")
    
    # Configure methods to use MockIOCapture
    def display_system_message(message):
        print(f"[SYSTEM] {message}")
    
    def display_user_message(message):
        print(f"[USER] {message}")
    
    def display_assistant_message(message):
        print(f"[ASSISTANT] {message}")
    
    def display_error_message(error_type, message):
        print(f"[ERROR:{error_type}] {message}")
    
    def display_special_command_help(commands):
        print("[HELP] Available commands:")
        for cmd, desc in commands.items():
            print(f"  {cmd}: {desc}")
    
    def get_user_input():
        return mock_io_capture.mock_input("[INPUT] ")
    
    mock_manager.display_system_message.side_effect = display_system_message
    mock_manager.display_user_message.side_effect = display_user_message
    mock_manager.display_assistant_message.side_effect = display_assistant_message
    mock_manager.display_error_message.side_effect = display_error_message
    mock_manager.display_special_command_help.side_effect = display_special_command_help
    mock_manager.get_user_input.side_effect = get_user_input
    
    return mock_manager


@pytest.fixture
def mock_tool_request_handler(mock_teps_manager):
    """Provide a mock ToolRequestHandler instance."""
    mock_handler = MagicMock(name="ToolRequestHandler")
    
    # Configure process_tool_request to delegate to teps_manager
    mock_handler.process_tool_request.side_effect = lambda tool_request: (
        mock_teps_manager.execute_tool(tool_request)
    )
    
    # Configure format_tool_result_as_message with common formatting
    def format_tool_result_as_message(tool_result):
        import json
        
        # Extract data
        tool_name = tool_result.get("tool_name", "unknown")
        request_id = tool_result.get("request_id", "unknown")
        content = tool_result.get("data", {})
        
        # Format content as string if needed
        if not isinstance(content, str):
            try:
                content = json.dumps(content)
            except:
                content = str(content)
        
        return {
            "role": "tool_result",
            "content": content,
            "tool_name": tool_name,
            "tool_call_id": request_id
        }
    
    mock_handler.format_tool_result_as_message.side_effect = format_tool_result_as_message
    
    return mock_handler


@pytest.fixture
def mock_error_handler():
    """Provide a mock ErrorHandler instance."""
    mock_handler = MagicMock(name="ErrorHandler")
    
    # Configure handle_error with common behavior
    def handle_error(error_type, message, exception=None):
        formatted_message = f"{error_type}: {message}"
        if exception:
            formatted_message += f" ({type(exception).__name__})"
        return formatted_message
    
    mock_handler.handle_error.side_effect = handle_error
    
    return mock_handler


@pytest.fixture
def mock_config_manager(mock_complete_config):
    """Provide a mock ConfigurationManager instance."""
    mock_manager = MagicMock(name="ConfigurationManager")
    
    # Set the config attribute
    mock_manager.config = mock_complete_config
    
    # Configure getter methods
    mock_manager.get_context_definition_path.return_value = mock_complete_config["context_definition_file"]
    mock_manager.get_llm_provider.return_value = mock_complete_config["llm_provider"]
    mock_manager.get_llm_settings.return_value = mock_complete_config["llm_settings"]
    mock_manager.get_teps_settings.return_value = mock_complete_config["teps_settings"]
    mock_manager.get_message_history_settings.return_value = mock_complete_config["message_history_settings"]
    mock_manager.get_ui_settings.return_value = mock_complete_config["ui_settings"]
    
    return mock_manager


# Faker component mocks

@pytest.fixture
def framework_controller_factory(
    mock_config_manager,
    mock_dcm_manager,
    mock_lial_manager,
    mock_teps_manager,
    mock_message_manager,
    mock_ui_manager,
    mock_tool_request_handler,
    mock_error_handler
):
    """Factory function to create a fresh FrameworkController instance with mock components."""
    def create_controller():
        from framework_core.controller import FrameworkController
        
        # Create a new controller with the mock config manager
        controller = FrameworkController(mock_config_manager)
        
        # Replace error handler
        controller.error_handler = mock_error_handler
        
        # Replace components
        controller.dcm_manager = mock_dcm_manager
        controller.lial_manager = mock_lial_manager
        controller.teps_manager = mock_teps_manager
        controller.message_manager = mock_message_manager
        controller.ui_manager = mock_ui_manager
        controller.tool_request_handler = mock_tool_request_handler
        
        return controller
    
    return create_controller


@pytest.fixture
def pyfakefs_for_teps(fs):
    """Set up a fake filesystem for TEPS testing."""
    # Create common test directories and files
    fs.create_dir('/home/user')
    fs.create_dir('/tmp')
    fs.create_dir('/path/to')
    
    # Create test files
    fs.create_file('/path/to/file.txt', contents='This is a test file.')
    fs.create_file('/path/to/config.yaml', contents='key: value\nlist:\n  - item1\n  - item2')
    
    return fs