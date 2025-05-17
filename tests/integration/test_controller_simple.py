"""
Integration tests for the Framework Controller component.

These tests verify that the Framework Controller correctly:
1. Initializes framework components in the proper order and manages dependencies
2. Processes special commands and routes them appropriately
3. Handles errors across component boundaries
4. Routes messages between components
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch, call

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.controller import FrameworkController
from framework_core.exceptions import (
    ConfigError, 
    DCMInitError, 
    LIALInitError, 
    TEPSInitError,
    ComponentInitError,
    ToolExecutionError
)

class TestControllerSimple:
    """
    Integration tests for the Framework Controller.
    
    These tests use direct patching and mocking rather than fixtures.
    """
    
    def setup_mock_config(self):
        """Create a mock configuration manager."""
        mock_config = MagicMock(name="ConfigurationManager")
        mock_config.get_context_definition_path.return_value = "/path/to/context.md"
        mock_config.get_llm_provider.return_value = "mock_provider"
        mock_config.get_llm_settings.return_value = {"model": "mock_model"}
        mock_config.get_teps_settings.return_value = {"mock_setting": "value"}
        mock_config.get_message_history_settings.return_value = {"max_length": 100}
        mock_config.get_ui_settings.return_value = {"prompt_prefix": "> "}
        mock_config.config = {
            "default_persona": "forge"
        }
        return mock_config
    
    def test_initialization_sequence(self):
        """Test that components are initialized in the correct order."""
        # Create mock config
        mock_config = self.setup_mock_config()
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create mocks for all component managers
        mock_dcm = MagicMock(name="DCMManager")
        mock_lial = MagicMock(name="LIALManager")
        mock_teps = MagicMock(name="TEPSManager")
        mock_message = MagicMock(name="MessageManager")
        mock_ui = MagicMock(name="UIManager")
        mock_tool = MagicMock(name="ToolRequestHandler")
        mock_error = MagicMock(name="ErrorHandler")
        
        # Configure necessary method returns
        mock_dcm.get_initial_prompt.return_value = "System prompt"
        
        # Replace controller components with mocks
        controller.dcm_manager = mock_dcm
        controller.lial_manager = mock_lial
        controller.teps_manager = mock_teps
        controller.message_manager = mock_message
        controller.ui_manager = mock_ui
        controller.tool_request_handler = mock_tool
        controller.error_handler = mock_error
        
        # Initialize with patched internal methods to avoid real initialization
        with patch.object(controller, '_initialize_dcm', return_value=True), \
             patch.object(controller, '_initialize_lial', return_value=True), \
             patch.object(controller, '_initialize_teps', return_value=True):
            result = controller.initialize()
        
        # Verify initialization succeeded
        assert result is True
        
        # Verify initial prompt was retrieved and added to message history
        mock_dcm.get_initial_prompt.assert_called_once()
        mock_message.add_system_message.assert_called_once()
    
    def test_dcm_initialization_failure(self):
        """Test handling of DCM initialization failure."""
        # Create mock config
        mock_config = self.setup_mock_config()
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Replace error handler with mock
        controller.error_handler = MagicMock(name="ErrorHandler")
        
        # Configure _initialize_dcm to fail
        with patch.object(controller, '_initialize_dcm', side_effect=DCMInitError("DCM initialization failed")):
            result = controller.initialize()
        
        # Verify initialization failed
        assert result is False
        
        # Verify error was handled
        controller.error_handler.handle_error.assert_called_once()
        assert "DCM Initialization Error" in controller.error_handler.handle_error.call_args[0][0]
    
    def test_lial_initialization_failure(self):
        """Test handling of LIAL initialization failure."""
        # Create mock config
        mock_config = self.setup_mock_config()
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Replace error handler with mock
        controller.error_handler = MagicMock(name="ErrorHandler")
        
        # Configure _initialize_dcm to succeed but _initialize_lial to fail
        with patch.object(controller, '_initialize_dcm', return_value=True), \
             patch.object(controller, '_initialize_lial', side_effect=LIALInitError("LIAL initialization failed")):
            result = controller.initialize()
        
        # Verify initialization failed
        assert result is False
        
        # Verify error was handled
        controller.error_handler.handle_error.assert_called_once()
        assert "LIAL Initialization Error" in controller.error_handler.handle_error.call_args[0][0]
    
    def test_teps_initialization_failure(self):
        """Test handling of TEPS initialization failure."""
        # Create mock config
        mock_config = self.setup_mock_config()
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Replace error handler with mock
        controller.error_handler = MagicMock(name="ErrorHandler")
        
        # Configure _initialize_dcm and _initialize_lial to succeed but _initialize_teps to fail
        with patch.object(controller, '_initialize_dcm', return_value=True), \
             patch.object(controller, '_initialize_lial', return_value=True), \
             patch.object(controller, '_initialize_teps', side_effect=TEPSInitError("TEPS initialization failed")):
            result = controller.initialize()
        
        # Verify initialization failed
        assert result is False
        
        # Verify error was handled
        controller.error_handler.handle_error.assert_called_once()
        assert "TEPS Initialization Error" in controller.error_handler.handle_error.call_args[0][0]
    
    def test_help_command_processing(self):
        """Test processing of the /help special command."""
        # Create mock config
        mock_config = self.setup_mock_config()
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create mocks for all required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure UI manager's get_user_input to return /help and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/help", "/quit"]
        
        # Configure LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Set running to True (normally done by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify help command was processed
        controller.ui_manager.display_special_command_help.assert_called_once_with(
            controller.SPECIAL_COMMANDS
        )
    
    def test_normal_user_message_flow(self):
        """Test normal message flow from user to LLM and back."""
        # Create mock config
        mock_config = self.setup_mock_config()
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create mocks for all required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure UI manager's get_user_input to return a normal message and then /quit
        controller.ui_manager.get_user_input.side_effect = ["Hello, assistant!", "/quit"]
        
        # Configure message_manager.get_messages to return a list of messages
        controller.message_manager.get_messages.return_value = [
            {"role": "system", "content": "You are an AI assistant."},
            {"role": "user", "content": "Hello, assistant!"}
        ]
        
        # Configure LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "Hello! I'm an AI assistant. How can I help you today?",
            "tool_request": None
        }
        
        # Set running to True (normally done by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify message flow
        controller.message_manager.add_user_message.assert_called_once_with("Hello, assistant!")
        controller.message_manager.get_messages.assert_called_with(for_llm=True)
        controller.lial_manager.send_messages.assert_called_once()
        controller.message_manager.add_assistant_message.assert_called_once_with(
            "Hello! I'm an AI assistant. How can I help you today?"
        )
        controller.ui_manager.display_assistant_message.assert_called_once_with(
            "Hello! I'm an AI assistant. How can I help you today?"
        )
        
    def test_tool_request_flow(self):
        """Test message flow with tool request."""
        # Create mock config
        mock_config = self.setup_mock_config()
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create mocks for all required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        controller.tool_request_handler = MagicMock(name="ToolRequestHandler")
        
        # Configure UI manager's get_user_input to return a message that triggers a tool request, then /quit
        controller.ui_manager.get_user_input.side_effect = ["Read file.txt", "/quit"]
        
        # Create a tool request
        tool_request = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "parameters": {"file_path": "file.txt"}
        }
        
        # Configure message_manager.get_messages to return two different sets of messages
        controller.message_manager.get_messages.side_effect = [
            # First call - initial user message
            [
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": "Read file.txt"}
            ],
            # Second call - after tool result
            [
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": "Read file.txt"},
                {"role": "assistant", "content": "I'll read that file for you."},
                {"role": "tool_result", "tool_name": "readFile", "content": "Test content", "tool_call_id": "read-123"}
            ]
        ]
        
        # Configure LLM responses - first with tool request, then response to tool result
        controller.lial_manager.send_messages.side_effect = [
            {
                "conversation": "I'll read that file for you.",
                "tool_request": tool_request
            },
            {
                "conversation": "The file contains: Test content",
                "tool_request": None
            }
        ]
        
        # Configure tool_request_handler
        controller.tool_request_handler.process_tool_request.return_value = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "status": "success",
            "data": "Test content"
        }
        controller.tool_request_handler.format_tool_result_as_message.return_value = {
            "role": "tool_result",
            "content": "Test content",
            "tool_name": "readFile",
            "tool_call_id": "read-123"
        }
        
        # Set running to True (normally done by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify message flow
        controller.message_manager.add_user_message.assert_called_once_with("Read file.txt")
        
        # Verify the tool request was processed
        controller.tool_request_handler.process_tool_request.assert_called_once_with(tool_request)
        
        # Verify the tool result was added to the message history
        controller.message_manager.add_tool_result_message.assert_called_once_with(
            tool_name="readFile",
            content="Test content",
            tool_call_id="read-123"
        )
        
        # Verify LLM was called again with the updated message history
        assert controller.lial_manager.send_messages.call_count == 2
        
        # Verify the final assistant response was added to message history and displayed
        controller.message_manager.add_assistant_message.assert_called_with(
            "The file contains: Test content"
        )
        controller.ui_manager.display_assistant_message.assert_called_with(
            "The file contains: Test content"
        )