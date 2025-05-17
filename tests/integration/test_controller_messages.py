"""
Integration tests for the Framework Controller message handling and error handling.

These tests verify that the Framework Controller correctly handles:
1. Normal user message flow
2. Tool request flow
3. Error conditions
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch, call

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.controller import FrameworkController
from framework_core.exceptions import ToolExecutionError

class TestControllerMessages:
    """
    Integration tests for Framework Controller message and error handling.
    """
    
    def test_process_messages_with_llm(self):
        """Test processing messages with LLM via LIAL."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        mock_config.config = {"default_persona": "forge"}
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create mock LIAL manager
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure messages
        messages = [
            {"role": "system", "content": "You are an AI assistant."},
            {"role": "user", "content": "Hello, assistant!"}
        ]
        
        # Configure LLM response
        expected_response = {
            "conversation": "Hello! I'm an AI assistant. How can I help you today?",
            "tool_request": None
        }
        controller.lial_manager.send_messages.return_value = expected_response
        
        # Call the method directly
        result = controller._process_messages_with_llm(messages)
        
        # Verify the response
        assert result == expected_response
        controller.lial_manager.send_messages.assert_called_once_with(messages, active_persona_id="forge")
    
    def test_handle_tool_request(self):
        """Test handling a tool request via the Tool Request Handler."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create and attach mocks for required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.tool_request_handler = MagicMock(name="ToolRequestHandler")
        
        # Create a tool request
        tool_request = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "parameters": {"file_path": "file.txt"}
        }
        
        # Configure tool request handler
        tool_result = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "status": "success",
            "data": "Test content"
        }
        controller.tool_request_handler.process_tool_request.return_value = tool_result
        
        formatted_result = {
            "role": "tool_result",
            "content": "Test content",
            "tool_name": "readFile",
            "tool_call_id": "read-123"
        }
        controller.tool_request_handler.format_tool_result_as_message.return_value = formatted_result
        
        # Enable debug mode to test that path
        controller.debug_mode = True
        
        # Call the method directly
        controller._handle_tool_request(tool_request)
        
        # Verify tool request was processed
        controller.tool_request_handler.process_tool_request.assert_called_once_with(tool_request)
        
        # Verify tool result was formatted
        controller.tool_request_handler.format_tool_result_as_message.assert_called_once_with(tool_result)
        
        # Verify tool result was added to message history
        controller.message_manager.add_tool_result_message.assert_called_once_with(
            tool_name="readFile",
            content="Test content",
            tool_call_id="read-123"
        )
        
        # Verify debug message was displayed since debug mode is enabled
        controller.ui_manager.display_system_message.assert_called_once()
        
    def test_handle_tool_execution_error(self):
        """Test handling of tool execution errors."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create and attach mocks for required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.tool_request_handler = MagicMock(name="ToolRequestHandler")
        controller.error_handler = MagicMock(name="ErrorHandler")
        
        # Create a tool request
        tool_request = {
            "request_id": "bash-123",
            "tool_name": "executeBashCommand",
            "parameters": {"command": "invalid_command"}
        }
        
        # Configure error handler
        controller.error_handler.handle_error.return_value = "Handled error: Command not found"
        
        # Configure tool request handler to raise an error
        error_result = {
            "request_id": "bash-123",
            "tool_name": "executeBashCommand",
            "status": "error",
            "data": {"error_message": "Command not found: invalid_command"}
        }
        
        controller.tool_request_handler.process_tool_request.side_effect = ToolExecutionError(
            "Command not found: invalid_command",
            error_result=error_result
        )
        
        # Call the method directly
        controller._handle_tool_request(tool_request)
        
        # Verify error was handled
        controller.error_handler.handle_error.assert_called_once()
        assert "Tool Execution Error" in controller.error_handler.handle_error.call_args[0][0]
        
        # Verify error was displayed to user
        controller.ui_manager.display_error_message.assert_called_once()
        
        # Verify error result was added to message history
        controller.message_manager.add_tool_result_message.assert_called_once()
        # Verify error content in message
        assert "error" in controller.message_manager.add_tool_result_message.call_args[1]["content"].lower()
    
    def test_process_messages_with_llm_error_handling(self):
        """Test error handling in the process_messages_with_llm method."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create mocks for required components
        controller.lial_manager = MagicMock(name="LIALManager")
        controller.error_handler = MagicMock(name="ErrorHandler")
        
        # Configure LLM to raise an exception
        controller.lial_manager.send_messages.side_effect = Exception("Runtime error")
        
        # Call the method directly
        messages = [{"role": "user", "content": "Hello"}]
        result = controller._process_messages_with_llm(messages)
        
        # Verify error handling
        assert "conversation" in result
        assert "error" in result["conversation"].lower()
        assert "tool_request" in result
        assert result["tool_request"] is None