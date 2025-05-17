"""
End-to-end tests for special commands and error handling.

These tests verify that the framework correctly:
1. Processes special commands in realistic conversation flows
2. Handles various error conditions gracefully
3. Manages command sequences and combinations
4. Provides appropriate user feedback for commands and errors
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch, call

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.integration.utils import IntegrationTestCase
from tests.integration.e2e_fixtures import (
    ConversationScenario, 
    MockScenarioBuilder,
    assert_system_message_added,
    assert_error_handled
)


class TestE2ESpecialCommands(IntegrationTestCase):
    """
    End-to-end tests for special command processing.
    
    These tests verify the framework's ability to handle special commands
    in realistic conversation flows.
    """
    
    def test_help_command(self, e2e_controller, mock_conversation):
        """Test processing of /help command."""
        # Create a scenario for help command
        scenario = ConversationScenario(
            name="help_command",
            description="Help command processing"
        ).add_user_input(
            "/help"
        ).add_user_input(
            "What can you do?"
        ).add_expected_llm_response(
            "I'm an AI assistant that can help with various tasks. I can answer questions, "
            "assist with coding, read and write files, and execute commands. "
            "Is there something specific you'd like help with?"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify help was displayed
        controller.ui_manager.display_special_command_help.assert_called_once_with(
            controller.SPECIAL_COMMANDS
        )
        
        # Verify no message was added for the /help command
        assert controller.message_manager.add_user_message.call_count == 1
    
    def test_system_command(self, e2e_controller, mock_conversation):
        """Test processing of /system command."""
        # Create a system message
        system_message = "You are an assistant that specializes in Python programming."
        
        # Create a scenario for system command
        scenario = ConversationScenario(
            name="system_command",
            description="System command processing"
        ).add_user_input(
            f"/system {system_message}"
        ).add_user_input(
            "What programming language do you specialize in?"
        ).add_expected_llm_response(
            "I specialize in Python programming. I can help you with Python code, libraries, "
            "best practices, debugging, and more. What Python-related question do you have?"
        ).add_verification_step(
            lambda controller: assert_system_message_added(controller, system_message),
            "Verify system message was added"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify system message was added
        assert controller.message_manager.add_system_message.call_count >= 1
        
        # Verify system command confirmation was displayed
        system_displays = [
            call for call in controller.ui_manager.display_system_message.call_args_list
            if f"Added system message: {system_message}" in call[0][0]
        ]
        assert len(system_displays) >= 1
    
    def test_clear_command(self, e2e_controller, mock_conversation):
        """Test processing of /clear command."""
        # Create a scenario for clear command
        scenario = ConversationScenario(
            name="clear_command",
            description="Clear command processing"
        ).add_user_input(
            "This is a message before clearing"
        ).add_expected_llm_response(
            "I've received your message before clearing."
        ).add_user_input(
            "/clear"
        ).add_user_input(
            "This is a message after clearing"
        ).add_expected_llm_response(
            "I've received your message after clearing."
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify history was cleared
        controller.message_manager.clear_history.assert_called_once_with(preserve_system=True)
        
        # Verify clear confirmation was displayed
        clear_displays = [
            call for call in controller.ui_manager.display_system_message.call_args_list
            if "Conversation history cleared" in call[0][0]
        ]
        assert len(clear_displays) >= 1
    
    def test_debug_command(self, e2e_controller, mock_conversation):
        """Test processing of /debug command."""
        # Create a scenario for debug command
        scenario = ConversationScenario(
            name="debug_command",
            description="Debug command processing"
        ).add_user_input(
            "/debug"
        ).add_user_input(
            "Is debug mode on?"
        ).add_expected_llm_response(
            "Yes, debug mode is currently enabled. This means I'll provide more detailed information "
            "about internal operations, particularly when using tools."
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Ensure debug mode starts as False
        controller.debug_mode = False
        
        # Run the controller
        controller.run()
        
        # Verify debug mode was toggled
        assert controller.debug_mode is True
        
        # Verify debug mode confirmation was displayed
        debug_displays = [
            call for call in controller.ui_manager.display_system_message.call_args_list
            if "Debug mode enabled" in call[0][0]
        ]
        assert len(debug_displays) >= 1
    
    def test_command_sequence(self, e2e_controller, mock_conversation):
        """Test a sequence of multiple commands."""
        # Create a scenario with a sequence of commands
        scenario = ConversationScenario(
            name="command_sequence",
            description="Command sequence processing"
        ).add_user_input(
            "/system You are a helpful assistant."
        ).add_user_input(
            "/debug"
        ).add_user_input(
            "/clear"
        ).add_user_input(
            "Did all the commands work?"
        ).add_expected_llm_response(
            "Yes, all the commands were successfully processed. I've added the system message, "
            "enabled debug mode, and cleared the conversation history."
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify all commands were processed
        assert controller.message_manager.add_system_message.call_count >= 1
        assert controller.message_manager.clear_history.call_count >= 1
        assert controller.debug_mode is True
    
    def test_unknown_command(self, e2e_controller, mock_conversation):
        """Test handling of unknown command."""
        # Create a scenario with an unknown command
        scenario = ConversationScenario(
            name="unknown_command",
            description="Unknown command processing"
        ).add_user_input(
            "/unknowncommand"
        ).add_user_input(
            "Did that work?"
        ).add_expected_llm_response(
            "No, the previous command '/unknowncommand' was not recognized. "
            "If you need help with available commands, you can use the /help command."
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify error message was displayed
        controller.ui_manager.display_error_message.assert_called_with(
            "Command Error", "Unknown command: /unknowncommand"
        )


class TestE2EErrorHandling(IntegrationTestCase):
    """
    End-to-end tests for error handling.
    
    These tests verify the framework's ability to handle various error
    conditions gracefully in realistic scenarios.
    """
    
    def test_llm_api_error(self, e2e_controller, mock_conversation):
        """Test handling of LLM API errors."""
        # Create a scenario where the LLM raises an error
        scenario = ConversationScenario(
            name="llm_api_error",
            description="LLM API error handling"
        ).add_user_input(
            "This will cause an API error"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Configure LLM to raise an exception
        controller.lial_manager.send_messages.side_effect = Exception("LLM API Error")
        
        # Run the controller
        controller.run()
        
        # Verify error was handled
        assert controller.error_handler.handle_error.call_count >= 1
        assert controller.ui_manager.display_error_message.call_count >= 1
        
        # Extract error message
        error_displays = controller.ui_manager.display_error_message.call_args_list
        assert any("Runtime Error" in call[0][0] for call in error_displays)
    
    def test_malformed_llm_response(self, e2e_controller, mock_conversation):
        """Test handling of malformed LLM responses."""
        # Create a scenario with malformed LLM response
        scenario = ConversationScenario(
            name="malformed_response",
            description="Malformed LLM response handling"
        ).add_user_input(
            "This will return a malformed response"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Configure LLM to return invalid response types in sequence
        controller.lial_manager.send_messages.side_effect = [
            "This is a string, not a dict",  # First response is a string
            {"conversation": "I've recovered now.", "tool_request": None}  # Second is valid
        ]
        
        # Run the controller
        controller.run()
        
        # Verify the controller handles malformed response
        assert controller.message_manager.add_assistant_message.call_count >= 1
        
        # The response should contain a message about an issue
        call_args = controller.message_manager.add_assistant_message.call_args_list[0][0]
        assert "issue" in call_args[0].lower()
    
    def test_keyboard_interrupt(self, e2e_controller, mock_conversation):
        """Test handling of keyboard interrupts."""
        # Create a scenario where keyboard interrupt occurs
        scenario = ConversationScenario(
            name="keyboard_interrupt",
            description="Keyboard interrupt handling"
        ).add_user_input(
            "This will be interrupted"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Configure UI manager to raise KeyboardInterrupt and then return normally
        controller.ui_manager.get_user_input.side_effect = [
            KeyboardInterrupt,
            "After interrupt",
            "/quit"
        ]
        
        # Run the controller
        controller.run()
        
        # Verify interrupt message was displayed
        interrupt_displays = [
            call for call in controller.ui_manager.display_system_message.call_args_list
            if "Interrupted" in call[0][0]
        ]
        assert len(interrupt_displays) >= 1
    
    def test_multiple_errors(self, e2e_controller, mock_conversation):
        """Test handling of multiple errors in sequence."""
        # Create a scenario with multiple errors
        scenario = ConversationScenario(
            name="multiple_errors",
            description="Multiple error handling"
        ).add_user_input(
            "This will cause an error"
        ).add_user_input(
            "This will work normally"
        ).add_expected_llm_response(
            "I've recovered from the previous errors and am working normally now."
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Configure LLM to raise an exception and then return normally
        controller.lial_manager.send_messages.side_effect = [
            Exception("First error"),
            {"conversation": "I've recovered from the previous errors and am working normally now.", "tool_request": None}
        ]
        
        # Run the controller
        controller.run()
        
        # Verify both errors were handled and recovery occurred
        assert controller.error_handler.handle_error.call_count >= 1
        assert controller.message_manager.add_assistant_message.call_count >= 1
    
    def test_component_not_initialized(self, e2e_controller, mock_conversation):
        """Test handling of uninitialized component errors."""
        # Create a basic scenario
        scenario = ConversationScenario(
            name="component_not_initialized",
            description="Uninitialized component error handling"
        ).add_user_input(
            "Hello with uninitialized components"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Set a key component to None to simulate uninitialized component
        controller.lial_manager = None
        
        # We expect run() to raise ComponentInitError
        with pytest.raises(ComponentInitError):
            controller.run()
    
    def test_empty_and_small_inputs(self, e2e_controller, mock_conversation):
        """Test handling of empty and very small inputs."""
        # Create a scenario with empty and small inputs
        scenario = ConversationScenario(
            name="empty_small_inputs",
            description="Empty and small input handling"
        ).add_user_input(
            ""  # Empty input
        ).add_user_input(
            "a"  # Single character
        ).add_expected_llm_response(
            "I notice your input was very brief. Could you please provide more details or context about what you'd like help with?"
        ).add_user_input(
            "Now a normal message"
        ).add_expected_llm_response(
            "Thank you for providing more details. How can I assist you with that?"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Empty input should be ignored, only other inputs should be processed
        assert controller.message_manager.add_user_message.call_count == 2  # 'a' and 'normal message'