"""
Enhanced integration tests for the Framework Controller component.

These tests extend the existing test_controller.py with additional test cases to
ensure comprehensive coverage of the controller's functionality.
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


class TestControllerPersonaAndConfig(IntegrationTestCase):
    """
    Integration tests focusing on persona selection and configuration handling.
    """
    
    def test_active_persona_selection(self, framework_controller_factory):
        """Test that the active persona ID is correctly passed to LIAL."""
        # Create a controller instance
        controller = framework_controller_factory()
        
        # Configure default persona in config
        controller.config_manager.config = {"default_persona": "catalyst"}
        
        # Initialize the controller
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message and then /quit
        controller.ui_manager.get_user_input.side_effect = ["Hello", "/quit"]
        
        # Run the controller
        controller.run()
        
        # Verify that the active persona ID was passed to LIAL
        controller.lial_manager.send_messages.assert_called_once()
        call_args = controller.lial_manager.send_messages.call_args[1]
        assert "active_persona_id" in call_args
        assert call_args["active_persona_id"] == "catalyst"
    
    def test_default_persona_configuration(self, framework_controller_factory, mock_complete_config):
        """Test that the default persona is correctly loaded from configuration."""
        # Modify mock config to have a specific default persona
        mock_complete_config["default_persona"] = "forge"
        
        # Create a controller instance with this config
        controller = framework_controller_factory()
        controller.config_manager.config = mock_complete_config
        
        # Initialize the controller
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message and then /quit
        controller.ui_manager.get_user_input.side_effect = ["Hello", "/quit"]
        
        # Run the controller
        controller.run()
        
        # Verify that the default persona was used
        controller.lial_manager.send_messages.assert_called_once()
        call_args = controller.lial_manager.send_messages.call_args[1]
        assert call_args["active_persona_id"] == "forge"
    
    def test_configuration_loading(self, mock_complete_config):
        """Test that the controller correctly loads and uses configuration settings."""
        # Create a controller with the mock config
        from framework_core.config_loader import ConfigurationManager
        
        # Create a mock config manager that returns our mock config
        mock_config_manager = MagicMock(spec=ConfigurationManager)
        mock_config_manager.config = mock_complete_config
        mock_config_manager.get_context_definition_path.return_value = mock_complete_config["context_definition_file"]
        mock_config_manager.get_llm_provider.return_value = mock_complete_config["llm_provider"]
        mock_config_manager.get_llm_settings.return_value = mock_complete_config["llm_settings"]
        mock_config_manager.get_teps_settings.return_value = mock_complete_config["teps_settings"]
        mock_config_manager.get_message_history_settings.return_value = mock_complete_config["message_history_settings"]
        mock_config_manager.get_ui_settings.return_value = mock_complete_config["ui_settings"]
        
        # Create controller with this config
        controller = FrameworkController(mock_config_manager)
        
        # Mock the component managers
        controller.dcm_manager = MagicMock()
        controller.lial_manager = MagicMock()
        controller.teps_manager = MagicMock()
        
        # Initialize with patched methods to avoid real initialization
        with patch.object(controller, '_initialize_dcm', return_value=True), \
             patch.object(controller, '_initialize_lial', return_value=True), \
             patch.object(controller, '_initialize_teps', return_value=True):
            controller.initialize()
        
        # Verify configuration was used correctly
        mock_config_manager.get_context_definition_path.assert_called_once()
        mock_config_manager.get_llm_provider.assert_called_once()
        mock_config_manager.get_llm_settings.assert_called_once()
        mock_config_manager.get_teps_settings.assert_called_once()
        mock_config_manager.get_message_history_settings.assert_called_once()
        mock_config_manager.get_ui_settings.assert_called_once()


class TestControllerToolRequests(IntegrationTestCase):
    """
    Integration tests focusing on tool request handling.
    """
    
    def test_multiple_sequential_tool_requests(self, framework_controller_factory):
        """Test handling of multiple sequential tool requests without user input."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message that triggers tool requests, then /quit
        controller.ui_manager.get_user_input.side_effect = ["Run a series of commands", "/quit"]
        
        # Create tool requests
        tool_request_1 = {
            "request_id": "command-1",
            "tool_name": "executeBashCommand",
            "parameters": {"command": "ls"}
        }
        
        tool_request_2 = {
            "request_id": "command-2",
            "tool_name": "executeBashCommand",
            "parameters": {"command": "pwd"}
        }
        
        # Configure LLM responses for the sequence:
        # 1. First response with tool request 1
        # 2. Second response (after tool result 1) with tool request 2
        # 3. Third response (after tool result 2) with just conversation
        controller.lial_manager.send_messages.side_effect = [
            {
                "conversation": "I'll run the first command.",
                "tool_request": tool_request_1
            },
            {
                "conversation": "Now I'll run the second command.",
                "tool_request": tool_request_2
            },
            {
                "conversation": "I've completed all commands.",
                "tool_request": None
            }
        ]
        
        # Mock the tool request handler to return successful results
        controller.tool_request_handler.process_tool_request.side_effect = [
            {
                "request_id": "command-1",
                "tool_name": "executeBashCommand",
                "status": "success",
                "data": "file1.txt file2.txt"
            },
            {
                "request_id": "command-2",
                "tool_name": "executeBashCommand",
                "status": "success",
                "data": "/home/user"
            }
        ]
        
        # Mock the tool result formatting
        controller.tool_request_handler.format_tool_result_as_message.side_effect = [
            {
                "role": "tool_result",
                "content": "file1.txt file2.txt",
                "tool_name": "executeBashCommand",
                "tool_call_id": "command-1"
            },
            {
                "role": "tool_result",
                "content": "/home/user",
                "tool_name": "executeBashCommand",
                "tool_call_id": "command-2"
            }
        ]
        
        # Run the controller
        controller.run()
        
        # Verify the sequence of events
        assert controller.lial_manager.send_messages.call_count == 3
        assert controller.tool_request_handler.process_tool_request.call_count == 2
        assert controller.message_manager.add_tool_result_message.call_count == 2
        
        # Verify the tool requests were processed in the correct order
        controller.tool_request_handler.process_tool_request.assert_has_calls([
            call(tool_request_1),
            call(tool_request_2)
        ])
        
        # Verify all assistant messages were added to the history
        controller.message_manager.add_assistant_message.assert_has_calls([
            call("I'll run the first command."),
            call("Now I'll run the second command."),
            call("I've completed all commands.")
        ])
    
    def test_tool_request_handler_missing(self, framework_controller_factory):
        """Test behavior when the tool request handler is not initialized."""
        # Create a controller instance
        controller = framework_controller_factory()
        
        # Initialize but then set tool_request_handler to None
        controller.initialize()
        controller.tool_request_handler = None
        
        # Mock the UI manager's get_user_input to return a message that triggers a tool request, then /quit
        controller.ui_manager.get_user_input.side_effect = ["Read file.txt", "/quit"]
        
        # Create a tool request
        tool_request = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "parameters": {"file_path": "file.txt"}
        }
        
        # Configure LLM responses
        controller.lial_manager.send_messages.side_effect = [
            {
                "conversation": "I'll read that file for you.",
                "tool_request": tool_request
            },
            {
                "conversation": "I'm not able to read files right now.",
                "tool_request": None
            }
        ]
        
        # Run the controller
        controller.run()
        
        # Verify that no error occurred and the controller continued operation
        assert controller.lial_manager.send_messages.call_count == 2
        
        # Verify no tool result was added (since handler was missing)
        assert not controller.message_manager.add_tool_result_message.called


class TestControllerErrorHandling(IntegrationTestCase):
    """
    Integration tests focusing on error handling in the controller.
    """
    
    def test_invalid_llm_response_handling_not_dict(self, framework_controller_factory):
        """Test handling of invalid LLM responses (not a dictionary)."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message and then /quit
        controller.ui_manager.get_user_input.side_effect = ["Hello", "/quit"]
        
        # Configure LLM to return an invalid response (string instead of dict)
        controller.lial_manager.send_messages.return_value = "This is not a valid response"
        
        # Run the controller
        controller.run()
        
        # Verify that an error message was added to conversation
        controller.message_manager.add_assistant_message.assert_called_once()
        call_args = controller.message_manager.add_assistant_message.call_args[0]
        assert "issue" in call_args[0].lower()
    
    def test_invalid_llm_response_handling_missing_conversation(self, framework_controller_factory):
        """Test handling of invalid LLM responses (missing conversation key)."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Mock the UI manager's get_user_input to return a message and then /quit
        controller.ui_manager.get_user_input.side_effect = ["Hello", "/quit"]
        
        # Configure LLM to return a response missing the conversation key
        controller.lial_manager.send_messages.return_value = {
            "tool_request": None
            # Missing conversation key
        }
        
        # Run the controller
        controller.run()
        
        # Verify that a default message was added to conversation
        controller.message_manager.add_assistant_message.assert_called_once()
        call_args = controller.message_manager.add_assistant_message.call_args[0]
        assert "received" in call_args[0].lower()


class TestControllerComponentIntegration(IntegrationTestCase):
    """
    Integration tests focusing on the controller's integration with other components.
    """
    
    def test_dcm_integration(self, framework_controller_factory):
        """Test controller integration with DCM for context management."""
        # Create a controller instance
        controller = framework_controller_factory()
        
        # Configure DCM to return specific context
        controller.dcm_manager.get_initial_prompt.return_value = "Custom system prompt"
        controller.dcm_manager.get_persona_definitions.return_value = {
            "catalyst": "Catalyst persona definition",
            "forge": "Forge persona definition"
        }
        
        # Initialize the controller
        controller.initialize()
        
        # Verify DCM integration
        controller.dcm_manager.initialize.assert_called_once()
        controller.dcm_manager.get_initial_prompt.assert_called_once()
        
        # Verify initial context was set correctly
        controller.message_manager.add_system_message.assert_called_once_with("Custom system prompt")
    
    def test_lial_teps_integration_lifecycle(self, framework_controller_factory):
        """Test full lifecycle integration of controller with LIAL and TEPS."""
        # Create a controller instance
        controller = framework_controller_factory()
        
        # Initialize the controller
        controller.initialize()
        
        # Configure UI manager to return a user message that will trigger a tool request
        controller.ui_manager.get_user_input.side_effect = ["Execute command", "/quit"]
        
        # Configure messages from MessageManager
        controller.message_manager.get_messages.return_value = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Execute command"}
        ]
        
        # Configure LIAL to return a tool request
        tool_request = {
            "request_id": "cmd-123",
            "tool_name": "executeBashCommand",
            "parameters": {"command": "ls -la"}
        }
        controller.lial_manager.send_messages.side_effect = [
            {
                "conversation": "I'll execute that command.",
                "tool_request": tool_request
            },
            {
                "conversation": "The command has been executed successfully.",
                "tool_request": None
            }
        ]
        
        # Configure TEPS (via ToolRequestHandler) to return a result
        tool_result = {
            "request_id": "cmd-123",
            "tool_name": "executeBashCommand",
            "status": "success",
            "data": "total 8\ndrwxr-xr-x 2 user user 4096 May 17 10:00 ."
        }
        controller.tool_request_handler.process_tool_request.return_value = tool_result
        
        # Configure ToolRequestHandler to format the result
        formatted_result = {
            "role": "tool_result",
            "content": "total 8\ndrwxr-xr-x 2 user user 4096 May 17 10:00 .",
            "tool_name": "executeBashCommand",
            "tool_call_id": "cmd-123"
        }
        controller.tool_request_handler.format_tool_result_as_message.return_value = formatted_result
        
        # Run the controller
        controller.run()
        
        # Verify the full integration lifecycle
        controller.message_manager.add_user_message.assert_called_once_with("Execute command")
        controller.lial_manager.send_messages.assert_called()
        controller.tool_request_handler.process_tool_request.assert_called_once_with(tool_request)
        controller.tool_request_handler.format_tool_result_as_message.assert_called_once_with(tool_result)
        controller.message_manager.add_tool_result_message.assert_called_once()
        
        # Verify both assistant messages were added
        controller.message_manager.add_assistant_message.assert_has_calls([
            call("I'll execute that command."),
            call("The command has been executed successfully.")
        ])
        
        # Verify UI display
        controller.ui_manager.display_assistant_message.assert_has_calls([
            call("I'll execute that command."),
            call("The command has been executed successfully.")
        ])