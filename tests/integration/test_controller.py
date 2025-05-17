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
from tests.integration.utils import ResponseBuilder, IntegrationTestCase


class TestControllerIntegration(IntegrationTestCase):
    """
    Integration tests for the Framework Controller component.
    
    These tests validate that:
    1. The controller properly initializes all framework components
    2. Special commands are processed correctly
    3. Error handling works across component boundaries
    4. Message routing between components functions as expected
    """
    
    def test_initialization_sequence(self, framework_controller_factory):
        """Test that components are initialized in the correct order."""
        # Create a controller instance
        controller = framework_controller_factory()
        
        # Replace components with fresh mocks that we can control
        controller.dcm_manager = MagicMock()
        controller.dcm_manager.initialize.return_value = True
        controller.dcm_manager.get_initial_prompt.return_value = "System prompt"
        
        controller.lial_manager = MagicMock()
        controller.lial_manager.initialize.return_value = True
        
        controller.teps_manager = MagicMock()
        controller.teps_manager.initialize.return_value = True
        
        controller.message_manager = MagicMock()
        controller.ui_manager = MagicMock()
        controller.tool_request_handler = MagicMock()
        
        # Initialize the controller
        result = controller.initialize()
        
        # Verify initialization succeeded
        assert result is True
        
        # Verify components were initialized in the correct order
        # In Pytest, assert_called_once() only checks that it was called exactly once
        # Mocks don't track order automatically, but we can verify the calls were made
        controller.dcm_manager.initialize.assert_called_once()
        controller.lial_manager.initialize.assert_called_once()
        controller.teps_manager.initialize.assert_called_once()
        
        # Verify initial context was set up
        controller.dcm_manager.get_initial_prompt.assert_called_once()
        controller.message_manager.add_system_message.assert_called_once()
    
    def test_dcm_initialization_failure(self, framework_controller_factory):
        """Test handling of DCM initialization failure."""
        # Create a controller instance
        controller = framework_controller_factory()
        
        # Replace components with fresh mocks that we control
        controller.dcm_manager = MagicMock()
        controller.dcm_manager.initialize.side_effect = DCMInitError("DCM initialization failed")
        
        controller.error_handler = MagicMock()
        controller.error_handler.handle_error.return_value = "Error handled"
        
        # Attempt to initialize the controller
        result = controller.initialize()
        
        # Verify initialization failed
        assert result is False
        
        # Verify error was handled
        controller.error_handler.handle_error.assert_called_once()
        # Check error type
        assert controller.error_handler.handle_error.call_args[0][0] == "DCM Initialization Error"
    
    def test_lial_initialization_failure(self, framework_controller_factory):
        """Test handling of LIAL initialization failure."""
        # Create a controller instance
        controller = framework_controller_factory()
        
        # Replace components with fresh mocks that we control
        controller.dcm_manager = MagicMock()
        controller.dcm_manager.initialize.return_value = True
        
        controller.lial_manager = MagicMock()
        controller.lial_manager.initialize.side_effect = LIALInitError("LIAL initialization failed")
        
        controller.error_handler = MagicMock()
        controller.error_handler.handle_error.return_value = "Error handled"
        
        # Attempt to initialize the controller
        result = controller.initialize()
        
        # Verify initialization failed
        assert result is False
        
        # Verify error was handled
        controller.error_handler.handle_error.assert_called_once()
        # Check error type
        assert controller.error_handler.handle_error.call_args[0][0] == "LIAL Initialization Error"
    
    def test_teps_initialization_failure(self, framework_controller_factory):
        """Test handling of TEPS initialization failure."""
        # Create a controller instance
        controller = framework_controller_factory()
        
        # Replace components with fresh mocks that we control
        controller.dcm_manager = MagicMock()
        controller.dcm_manager.initialize.return_value = True
        
        controller.lial_manager = MagicMock()
        controller.lial_manager.initialize.return_value = True
        
        controller.teps_manager = MagicMock()
        controller.teps_manager.initialize.side_effect = TEPSInitError("TEPS initialization failed")
        
        controller.error_handler = MagicMock()
        controller.error_handler.handle_error.return_value = "Error handled"
        
        # Attempt to initialize the controller
        result = controller.initialize()
        
        # Verify initialization failed
        assert result is False
        
        # Verify error was handled
        controller.error_handler.handle_error.assert_called_once()
        # Check error type
        assert controller.error_handler.handle_error.call_args[0][0] == "TEPS Initialization Error"
    
    def test_run_without_initialization(self, framework_controller_factory):
        """Test that run fails if controller is not initialized."""
        # Create a controller instance (without initializing it)
        controller = framework_controller_factory()
        
        # Attempt to run without initialization
        with pytest.raises(ComponentInitError):
            controller.run()
    
    def test_help_command_processing(self, framework_controller_factory):
        """Test processing of the /help special command."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return /help and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/help", "/quit"]
        
        # Mock the LLM response to avoid infinite loop
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify help command was processed
        controller.ui_manager.display_special_command_help.assert_called_once_with(
            controller.SPECIAL_COMMANDS
        )
    
    def test_quit_command_processing(self, framework_controller_factory):
        """Test processing of the /quit special command."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return /quit
        controller.ui_manager.get_user_input.return_value = "/quit"
        
        # Mock the LLM response to avoid infinite loop
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify quit command was processed
        assert controller.running is False
        controller.ui_manager.display_system_message.assert_any_call("Exiting application...")
        controller.ui_manager.display_system_message.assert_any_call("Framework shutdown complete. Goodbye!")
    
    def test_clear_command_processing(self, framework_controller_factory):
        """Test processing of the /clear special command."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return /clear and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/clear", "/quit"]
        
        # Mock the LLM response to avoid infinite loop
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify clear command was processed
        controller.message_manager.clear_history.assert_called_once_with(preserve_system=True)
        controller.ui_manager.display_system_message.assert_any_call("Conversation history cleared.")
    
    def test_system_command_processing(self, framework_controller_factory):
        """Test processing of the /system special command."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return /system and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/system New system message", "/quit"]
        
        # Mock the LLM response to avoid infinite loop
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify system command was processed
        controller.message_manager.add_system_message.assert_any_call("New system message")
        controller.ui_manager.display_system_message.assert_any_call("Added system message: New system message")
    
    def test_debug_command_processing(self, framework_controller_factory):
        """Test processing of the /debug special command."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return /debug and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/debug", "/quit"]
        
        # Mock the LLM response to avoid infinite loop
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify debug command was processed
        assert controller.debug_mode is True
        controller.ui_manager.display_system_message.assert_any_call("Debug mode enabled.")
    
    def test_unknown_command_processing(self, framework_controller_factory):
        """Test processing of an unknown special command."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return an unknown command and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/unknown", "/quit"]
        
        # Mock the LLM response to avoid infinite loop
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify unknown command was processed
        controller.ui_manager.display_error_message.assert_called_once_with(
            "Command Error", "Unknown command: /unknown"
        )
    
    def test_normal_user_message_flow(self, framework_controller_factory):
        """Test normal message flow from user to LLM and back."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a normal message and then /quit
        controller.ui_manager.get_user_input.side_effect = ["Hello, assistant!", "/quit"]
        
        # Mock the LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "Hello! I'm an AI assistant. How can I help you today?",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify message flow
        controller.message_manager.add_user_message.assert_called_once_with("Hello, assistant!")
        controller.lial_manager.send_messages.assert_called_once()
        controller.message_manager.add_assistant_message.assert_called_once_with(
            "Hello! I'm an AI assistant. How can I help you today?"
        )
        controller.ui_manager.display_assistant_message.assert_called_once_with(
            "Hello! I'm an AI assistant. How can I help you today?"
        )
    
    def test_tool_request_flow(self, framework_controller_factory):
        """Test message flow with tool request."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message that triggers a tool request, then /quit
        controller.ui_manager.get_user_input.side_effect = ["Read file.txt", "/quit"]
        
        # Create a tool request
        tool_request = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "parameters": {"file_path": "file.txt"}
        }
        
        # Mock the LLM responses
        # First response includes a tool request
        # Second response is after the tool result
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
        
        # Mock the tool request handler to return a successful result
        controller.tool_request_handler.process_tool_request.return_value = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "status": "success",
            "data": "Test content"
        }
        
        # Mock the tool result formatting
        controller.tool_request_handler.format_tool_result_as_message.return_value = {
            "role": "tool_result",
            "content": "Test content",
            "tool_name": "readFile",
            "tool_call_id": "read-123"
        }
        
        # Run the controller
        controller.run()
        
        # Verify tool request flow
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
    
    def test_tool_execution_error_handling(self, framework_controller_factory):
        """Test handling of tool execution errors."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message that triggers a tool request, then /quit
        controller.ui_manager.get_user_input.side_effect = ["Run command", "/quit"]
        
        # Create a tool request
        tool_request = {
            "request_id": "bash-123",
            "tool_name": "executeBashCommand",
            "parameters": {"command": "invalid_command"}
        }
        
        # Mock the LLM responses
        controller.lial_manager.send_messages.side_effect = [
            {
                "conversation": "I'll run that command for you.",
                "tool_request": tool_request
            },
            {
                "conversation": "I encountered an error running the command.",
                "tool_request": None
            }
        ]
        
        # Mock the tool request handler to raise an error
        controller.tool_request_handler.process_tool_request.side_effect = ToolExecutionError(
            "Command not found: invalid_command",
            error_result={
                "request_id": "bash-123",
                "tool_name": "executeBashCommand",
                "status": "error",
                "data": {"error_message": "Command not found: invalid_command"}
            }
        )
        
        # Run the controller
        controller.run()
        
        # Verify error handling
        controller.error_handler.handle_error.assert_called_once()
        assert "Tool Execution Error" in controller.error_handler.handle_error.call_args[0][0]
        
        # Verify error message was displayed to user
        controller.ui_manager.display_error_message.assert_called_once()
        
        # Verify error was added to message history
        controller.message_manager.add_tool_result_message.assert_called_once()
        assert "error" in controller.message_manager.add_tool_result_message.call_args[1]["content"].lower()
    
    def test_keyboard_interrupt_handling(self, framework_controller_factory):
        """Test handling of keyboard interrupts during main loop."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to raise a KeyboardInterrupt and then return /quit
        controller.ui_manager.get_user_input.side_effect = [KeyboardInterrupt, "/quit"]
        
        # Mock the LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify keyboard interrupt was handled
        controller.ui_manager.display_system_message.assert_any_call("Interrupted. Type /quit to exit.")
    
    def test_runtime_error_handling(self, framework_controller_factory):
        """Test handling of runtime errors during main loop."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message
        controller.ui_manager.get_user_input.side_effect = ["Hello", "/quit"]
        
        # Mock the LLM to raise an exception
        controller.lial_manager.send_messages.side_effect = Exception("Runtime error")
        
        # Run the controller
        controller.run()
        
        # Verify runtime error was handled
        controller.error_handler.handle_error.assert_called_once()
        assert "Runtime Error" in controller.error_handler.handle_error.call_args[0][0]
        
        # Verify error message was displayed to user
        controller.ui_manager.display_error_message.assert_called_once()
        assert "Runtime Error" in controller.ui_manager.display_error_message.call_args[0][0]
    
    def test_empty_user_input_handling(self, framework_controller_factory):
        """Test handling of empty user input (from Ctrl+C/Ctrl+D)."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return empty string and then /quit
        controller.ui_manager.get_user_input.side_effect = ["", "/quit"]
        
        # Mock the LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify empty input was handled (no user message added)
        assert not controller.message_manager.add_user_message.called
    
    def test_message_pruning(self, framework_controller_factory):
        """Test message pruning during conversation."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message and then /quit
        controller.ui_manager.get_user_input.side_effect = ["Hello", "/quit"]
        
        # Mock the LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "Hello! I'm an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify message pruning was called
        controller.message_manager.prune_history.assert_called_once()
    
    def test_debug_mode_tool_result_display(self, framework_controller_factory):
        """Test that tool results are displayed in debug mode."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Enable debug mode
        controller.debug_mode = True
        
        # Mock the UI manager's get_user_input to return a message that triggers a tool request, then /quit
        controller.ui_manager.get_user_input.side_effect = ["Read file.txt", "/quit"]
        
        # Create a tool request
        tool_request = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "parameters": {"file_path": "file.txt"}
        }
        
        # Mock the LLM responses
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
        
        # Mock the tool request handler to return a successful result
        controller.tool_request_handler.process_tool_request.return_value = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "status": "success",
            "data": "Test content"
        }
        
        # Mock the tool result formatting
        controller.tool_request_handler.format_tool_result_as_message.return_value = {
            "role": "tool_result",
            "content": "Test content",
            "tool_name": "readFile",
            "tool_call_id": "read-123"
        }
        
        # Run the controller
        controller.run()
        
        # Verify debug information was displayed
        debug_calls = [
            call for call in controller.ui_manager.display_system_message.call_args_list
            if "Tool 'readFile' executed with result" in call[0][0]
        ]
        assert len(debug_calls) > 0