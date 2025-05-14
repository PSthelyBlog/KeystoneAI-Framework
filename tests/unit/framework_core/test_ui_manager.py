"""
Unit tests for the User Interface Manager.
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys

from framework_core.ui_manager import UserInterfaceManager

class TestUserInterfaceManager(unittest.TestCase):
    """Test cases for UserInterfaceManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "input_prompt": "$ ",
            "assistant_prefix": "[Bot]: ",
            "system_prefix": "[Sys]: ",
            "error_prefix": "[Err]: ",
            "use_color": False
        }
        
        # Create manager with mock handlers
        self.input_mock = MagicMock(return_value="mock user input")
        self.output_mock = MagicMock()
        
        self.manager = UserInterfaceManager(
            config=self.config,
            input_handler=self.input_mock,
            output_handler=self.output_mock
        )
        
    def test_display_assistant_message(self):
        """Test displaying assistant messages."""
        self.manager.display_assistant_message("Hello, user")
        
        # Check output_handler was called with formatted message
        self.output_mock.assert_called_once()
        arg = self.output_mock.call_args[0][0]
        self.assertTrue(arg.startswith("[Bot]: "))
        self.assertTrue("Hello, user" in arg)
        
    def test_display_system_message(self):
        """Test displaying system messages."""
        self.manager.display_system_message("System notification")
        
        # Check output_handler was called with formatted message
        self.output_mock.assert_called_once()
        arg = self.output_mock.call_args[0][0]
        self.assertTrue(arg.startswith("[Sys]: "))
        self.assertTrue("System notification" in arg)
        
    def test_display_error_message(self):
        """Test displaying error messages."""
        self.manager.display_error_message("ValidationError", "Invalid input")
        
        # Check output_handler was called with formatted message
        self.output_mock.assert_called_once()
        arg = self.output_mock.call_args[0][0]
        self.assertTrue(arg.startswith("[Err]: "))
        self.assertTrue("ValidationError" in arg)
        self.assertTrue("Invalid input" in arg)
        
    def test_get_user_input(self):
        """Test getting user input."""
        result = self.manager.get_user_input()
        
        # Check input_handler was called with configured prompt
        self.input_mock.assert_called_once_with("$ ")
        
        # Check result is returned from input_handler
        self.assertEqual(result, "mock user input")
        
        # Test with custom prompt
        self.input_mock.reset_mock()
        result = self.manager.get_user_input("Custom: ")
        self.input_mock.assert_called_once_with("Custom: ")
        
    def test_get_multiline_input(self):
        """Test getting multi-line input."""
        # Mock input to return three lines then end marker
        self.input_mock.side_effect = ["Line 1", "Line 2", "Line 3", "END"]
        
        result = self.manager.get_multiline_input(end_marker="END")
        
        # Check result contains all lines
        self.assertEqual(result, "Line 1\nLine 2\nLine 3")
        
        # Check input_handler was called four times
        self.assertEqual(self.input_mock.call_count, 4)
        
    def test_display_special_command_help(self):
        """Test displaying special command help."""
        commands = {
            "/help": "Show this help message",
            "/quit": "Exit the application",
            "/clear": "Clear conversation history"
        }
        
        self.manager.display_special_command_help(commands)
        
        # Check output_handler was called with formatted help
        self.output_mock.assert_called_once()
        arg = self.output_mock.call_args[0][0]
        
        # Check all commands are in the output
        for cmd in commands.keys():
            self.assertTrue(cmd in arg)
            
        # Check all descriptions are in the output
        for desc in commands.values():
            self.assertTrue(desc in arg)
            
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_default_output_handler(self, mock_stdout):
        """Test the default output handler."""
        # Create manager with default handlers
        manager = UserInterfaceManager(config=self.config)
        
        # Call internal method directly
        manager._default_output_handler("Test message")
        
        # Check output was written to stdout
        self.assertEqual(mock_stdout.getvalue().strip(), "Test message")
        
    @patch('builtins.input', return_value="User input")
    def test_default_input_handler(self, mock_input):
        """Test the default input handler."""
        # Create manager with default handlers
        manager = UserInterfaceManager(config=self.config)
        
        # Call internal method directly
        result = manager._default_input_handler("Prompt: ")
        
        # Check input was called with prompt
        mock_input.assert_called_once_with("Prompt: ")
        
        # Check result is returned from input
        self.assertEqual(result, "User input")
        
    def test_color_support_detection(self):
        """Test color support detection."""
        # This is hard to test definitively without mocking environment variables,
        # but we can at least test the method returns a boolean
        result = self.manager._supports_color()
        self.assertIsInstance(result, bool)
        
    def test_color_formatting(self):
        """Test color formatting when enabled."""
        # Create manager with color enabled
        color_manager = UserInterfaceManager(
            config={**self.config, "use_color": True},
            output_handler=self.output_mock
        )
        
        # Display message
        color_manager.display_assistant_message("Colored message")
        
        # Check message contains color codes
        arg = self.output_mock.call_args[0][0]
        self.assertTrue("\033[" in arg)  # Should contain ANSI color code

if __name__ == "__main__":
    unittest.main()