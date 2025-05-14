#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for the UI Manager component.

These tests verify that the UI Manager correctly integrates with the Controller
and other components to handle user input and output formatting.

AI-GENERATED: [Forge] - Task:[RFI-COREAPP-INT-TEST-001]
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch, call
import io

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.ui_manager import UserInterfaceManager
from framework_core.message_manager import MessageManager
from framework_core.controller import FrameworkController


class TestUIManagerIntegration(unittest.TestCase):
    """Integration tests for the UI Manager component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a UI Manager with customized input/output handlers
        self.input_mock = MagicMock()
        self.output_mock = MagicMock()
        
        self.ui_config = {
            "use_color": False,  # Disable colors for testing
            "input_prompt": "test> ",
            "assistant_prefix": "(Test-AI): ",
            "system_prefix": "[Test-System]: ",
            "error_prefix": "[Test-Error]: "
        }
        
        self.ui_manager = UserInterfaceManager(
            config=self.ui_config,
            input_handler=self.input_mock,
            output_handler=self.output_mock
        )
        
        # Create a Message Manager
        self.message_manager = MessageManager()
        
        # Create mock Controller components
        self.lial_manager = MagicMock()
        self.lial_manager.send_messages.return_value = {
            "conversation": "This is a mock LLM response.",
            "tool_request": None
        }
        
        self.dcm_manager = MagicMock()
        self.dcm_manager.get_initial_prompt.return_value = "You are a test AI assistant."
        
        self.teps_manager = MagicMock()
        
        # Create Controller with mocked components but real UI and Message managers
        self.controller = FrameworkController(MagicMock())
        self.controller.ui_manager = self.ui_manager
        self.controller.message_manager = self.message_manager
        self.controller.lial_manager = self.lial_manager
        self.controller.dcm_manager = self.dcm_manager
        self.controller.teps_manager = self.teps_manager
        self.controller.tool_request_handler = MagicMock()
    
    def test_ui_manager_display_integration(self):
        """Test that UI Manager correctly displays different message types."""
        # Test displaying system message
        self.ui_manager.display_system_message("System test message")
        self.output_mock.assert_called_with("[Test-System]: System test message")
        
        # Test displaying assistant message
        self.ui_manager.display_assistant_message("Assistant test message")
        self.output_mock.assert_called_with("(Test-AI): Assistant test message")
        
        # Test displaying error message
        self.ui_manager.display_error_message("Test Error", "This is a test error")
        self.output_mock.assert_called_with("[Test-Error]: Test Error: This is a test error")
        
        # Verify output order
        expected_calls = [
            call("[Test-System]: System test message"),
            call("(Test-AI): Assistant test message"),
            call("[Test-Error]: Test Error: This is a test error")
        ]
        self.output_mock.assert_has_calls(expected_calls)
    
    def test_user_input_processing_with_controller(self):
        """Test that user input is correctly processed through the controller."""
        # Configure input mock to simulate user input
        self.input_mock.side_effect = ["Test user input", KeyboardInterrupt()]
        
        # Run the controller main loop with expected early termination via KeyboardInterrupt
        try:
            self.controller.run()
        except KeyboardInterrupt:
            pass
        
        # Verify input was requested with the configured prompt
        self.input_mock.assert_called_with("test> ")
        
        # Verify the user message was added to the message history
        user_messages = [m for m in self.message_manager.messages if m["role"] == "user"]
        self.assertEqual(len(user_messages), 1)
        self.assertEqual(user_messages[0]["content"], "Test user input")
        
        # Verify LIAL was called with the messages
        self.lial_manager.send_messages.assert_called_once()
        
        # Verify the assistant response was added to the message history
        assistant_messages = [m for m in self.message_manager.messages if m["role"] == "assistant"]
        self.assertEqual(len(assistant_messages), 1)
        self.assertEqual(assistant_messages[0]["content"], "This is a mock LLM response.")
    
    def test_special_command_processing(self):
        """Test the processing of special commands through the UI Manager."""
        # Test help command
        self.input_mock.side_effect = ["/help", "/quit"]
        self.controller.run()
        
        # Verify help information was displayed
        help_calls = [call for call in self.output_mock.call_args_list 
                      if "[Test-System]:" in str(call) and "Available Commands" in str(call)]
        self.assertTrue(len(help_calls) > 0)
        
        # Reset mocks
        self.output_mock.reset_mock()
        
        # Test clear command
        self.input_mock.side_effect = ["/clear", "/quit"]
        self.controller.run()
        
        # Verify clear confirmation was displayed and messages were cleared
        clear_calls = [call for call in self.output_mock.call_args_list 
                       if "[Test-System]:" in str(call) and "Conversation history cleared" in str(call)]
        self.assertTrue(len(clear_calls) > 0)
        
        # Verify only system messages remain
        self.assertTrue(all(m["role"] == "system" for m in self.message_manager.messages))
    
    def test_multiline_input_handling(self):
        """Test handling of multiline input."""
        # Setup mock for input to simulate multiline entry
        self.input_mock.side_effect = ["```", "Line 1", "Line 2", "Line 3", "```", "/quit"]
        
        # Configure LLM response
        self.lial_manager.send_messages.return_value = {
            "conversation": "Received your multiline input",
            "tool_request": None
        }
        
        # Run the controller
        self.controller.run()
        
        # Check that the correct multiline content was added to message history
        user_messages = [m for m in self.message_manager.messages if m["role"] == "user"]
        
        # Expect one user message with three lines
        self.assertEqual(len(user_messages), 1)
        expected_content = "Line 1\nLine 2\nLine 3"
        self.assertEqual(user_messages[0]["content"], expected_content)
        
        # Verify LIAL was called with the correct message
        args, _ = self.lial_manager.send_messages.call_args
        sent_messages = args[0]
        
        # Find the user message in the sent messages
        sent_user_message = next((m for m in sent_messages if m["role"] == "user"), None)
        self.assertIsNotNone(sent_user_message)
        self.assertEqual(sent_user_message["content"], expected_content)
    
    def test_error_display_integration(self):
        """Test that errors are correctly displayed through the UI Manager."""
        # Configure LIAL to raise an exception
        self.lial_manager.send_messages.side_effect = Exception("Test LLM error")
        
        # Configure input
        self.input_mock.side_effect = ["Test input", "/quit"]
        
        # Run the controller
        self.controller.run()
        
        # Verify error was displayed
        error_calls = [call for call in self.output_mock.call_args_list 
                       if "[Test-Error]:" in str(call) and "Test LLM error" in str(call)]
        self.assertTrue(len(error_calls) > 0)
    
    def test_tool_request_display_integration(self):
        """Test that tool requests and results are correctly displayed through the UI Manager."""
        # Configure LIAL to return a tool request
        self.lial_manager.send_messages.side_effect = [
            {
                "conversation": "I'll execute that for you.",
                "tool_request": {
                    "request_id": "tool123",
                    "tool_name": "testTool",
                    "parameters": {"param": "value"}
                }
            },
            {
                "conversation": "Tool execution complete.",
                "tool_request": None
            }
        ]
        
        # Configure tool request handler
        self.controller.tool_request_handler.handle_tool_request.return_value = {
            "request_id": "tool123",
            "tool_name": "testTool",
            "status": "success",
            "data": {"result": "Tool execution succeeded"}
        }
        
        # Configure input
        self.input_mock.side_effect = ["Run test tool", "/quit"]
        
        # Run the controller
        self.controller.run()
        
        # Verify tool execution intent was displayed
        intent_calls = [call for call in self.output_mock.call_args_list 
                        if "(Test-AI): I'll execute that for you." in str(call)]
        self.assertTrue(len(intent_calls) > 0)
        
        # Verify tool result was added to message history
        tool_messages = [m for m in self.message_manager.messages if m["role"] == "tool_result"]
        self.assertEqual(len(tool_messages), 1)
        self.assertEqual(tool_messages[0]["tool_name"], "testTool")
        
        # Verify final message was displayed
        final_calls = [call for call in self.output_mock.call_args_list 
                       if "(Test-AI): Tool execution complete." in str(call)]
        self.assertTrue(len(final_calls) > 0)


if __name__ == "__main__":
    unittest.main()