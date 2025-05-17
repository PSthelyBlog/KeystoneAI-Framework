"""
Integration tests for the Framework Controller command processing.

These tests verify that the Framework Controller correctly processes special commands.
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch, call

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.controller import FrameworkController

class TestControllerCommands:
    """
    Integration tests for Framework Controller command processing.
    """
    
    def test_help_command_processing(self):
        """Test processing of the /help special command."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create and attach mocks for required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure UI manager to return /help and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/help", "/quit"]
        
        # Configure LLM response to avoid errors
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Set running flag to true (normally set by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify help command was processed
        controller.ui_manager.display_special_command_help.assert_called_once_with(
            controller.SPECIAL_COMMANDS
        )
    
    def test_quit_command_processing(self):
        """Test processing of the /quit special command."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create and attach mocks for required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure UI manager to return /quit
        controller.ui_manager.get_user_input.return_value = "/quit"
        
        # Set running flag to true (normally set by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify quit command was processed
        assert controller.running is False
        controller.ui_manager.display_system_message.assert_any_call("Exiting application...")
        controller.ui_manager.display_system_message.assert_any_call("Framework shutdown complete. Goodbye!")
    
    def test_clear_command_processing(self):
        """Test processing of the /clear special command."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create and attach mocks for required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure UI manager to return /clear and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/clear", "/quit"]
        
        # Configure LLM response to avoid errors
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Set running flag to true (normally set by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify clear command was processed
        controller.message_manager.clear_history.assert_called_once_with(preserve_system=True)
        controller.ui_manager.display_system_message.assert_any_call("Conversation history cleared.")
    
    def test_system_command_processing(self):
        """Test processing of the /system special command."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create and attach mocks for required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure UI manager to return /system message and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/system New system message", "/quit"]
        
        # Configure LLM response to avoid errors
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Set running flag to true (normally set by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify system command was processed
        controller.message_manager.add_system_message.assert_called_with("New system message")
        controller.ui_manager.display_system_message.assert_any_call("Added system message: New system message")
    
    def test_debug_command_processing(self):
        """Test processing of the /debug special command."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create and attach mocks for required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure UI manager to return /debug and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/debug", "/quit"]
        
        # Configure LLM response to avoid errors
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Set running flag to true (normally set by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify debug command was processed
        assert controller.debug_mode is True
        controller.ui_manager.display_system_message.assert_any_call("Debug mode enabled.")
    
    def test_unknown_command_processing(self):
        """Test processing of an unknown special command."""
        # Create mock components
        mock_config = MagicMock(name="ConfigurationManager")
        
        # Create controller with mock config
        controller = FrameworkController(mock_config)
        
        # Create and attach mocks for required components
        controller.message_manager = MagicMock(name="MessageManager")
        controller.ui_manager = MagicMock(name="UIManager")
        controller.lial_manager = MagicMock(name="LIALManager")
        
        # Configure UI manager to return an unknown command and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/unknown", "/quit"]
        
        # Configure LLM response to avoid errors
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Set running flag to true (normally set by initialize)
        controller.running = True
        
        # Run the controller
        controller.run()
        
        # Verify unknown command error is shown
        controller.ui_manager.display_error_message.assert_called_once_with(
            "Command Error", "Unknown command: /unknown"
        )