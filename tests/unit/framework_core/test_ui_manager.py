"""
Unit tests for the UserInterfaceManager class.

This module tests all the functionality of the UserInterfaceManager class
located in framework_core/ui_manager.py.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call

from framework_core.ui_manager import UserInterfaceManager


class TestUserInterfaceManager:
    """Test suite for the UserInterfaceManager class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        # Patch the _supports_color method to return a known value
        with patch.object(UserInterfaceManager, '_supports_color', return_value=True):
            ui_manager = UserInterfaceManager()
            
            # Check that default values are set correctly
            assert ui_manager.input_prompt == "> "
            assert ui_manager.assistant_prefix == "(AI): "
            assert ui_manager.system_prefix == "[System]: "
            assert ui_manager.error_prefix == "[Error]: "
            assert ui_manager.use_color is True
            
            # Check that handlers are set to default methods
            assert ui_manager.input_handler == ui_manager._default_input_handler
            assert ui_manager.output_handler == ui_manager._default_output_handler
    
    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        custom_config = {
            "input_prompt": "User: ",
            "assistant_prefix": "Assistant: ",
            "system_prefix": "System: ",
            "error_prefix": "Error: ",
            "use_color": False
        }
        
        ui_manager = UserInterfaceManager(config=custom_config)
        
        # Check that custom config values are set correctly
        assert ui_manager.input_prompt == "User: "
        assert ui_manager.assistant_prefix == "Assistant: "
        assert ui_manager.system_prefix == "System: "
        assert ui_manager.error_prefix == "Error: "
        assert ui_manager.use_color is False
    
    def test_init_with_custom_handlers(self):
        """Test initialization with custom input and output handlers."""
        # Create mock handlers
        mock_input_handler = MagicMock(return_value="Mock input")
        mock_output_handler = MagicMock()
        
        ui_manager = UserInterfaceManager(
            input_handler=mock_input_handler,
            output_handler=mock_output_handler
        )
        
        # Check that custom handlers are set correctly
        assert ui_manager.input_handler == mock_input_handler
        assert ui_manager.output_handler == mock_output_handler
    
    def test_display_assistant_message_with_color(self):
        """Test displaying an assistant message with color enabled."""
        mock_output_handler = MagicMock()
        
        # Create a UI manager with color enabled
        ui_manager = UserInterfaceManager(
            config={"use_color": True},
            output_handler=mock_output_handler
        )
        
        # Display a message
        ui_manager.display_assistant_message("Hello, I am an AI assistant.")
        
        # Check that the output handler was called with the correctly formatted message
        expected_prefix = f"{ui_manager.COLORS['green']}{ui_manager.COLORS['bold']}{ui_manager.assistant_prefix}{ui_manager.COLORS['reset']}"
        expected_message = f"{expected_prefix}Hello, I am an AI assistant."
        mock_output_handler.assert_called_once_with(expected_message)
    
    def test_display_assistant_message_without_color(self):
        """Test displaying an assistant message with color disabled."""
        mock_output_handler = MagicMock()
        
        # Create a UI manager with color disabled
        ui_manager = UserInterfaceManager(
            config={"use_color": False},
            output_handler=mock_output_handler
        )
        
        # Display a message
        ui_manager.display_assistant_message("Hello, I am an AI assistant.")
        
        # Check that the output handler was called with the correctly formatted message
        expected_message = f"{ui_manager.assistant_prefix}Hello, I am an AI assistant."
        mock_output_handler.assert_called_once_with(expected_message)
    
    def test_display_system_message_with_color(self):
        """Test displaying a system message with color enabled."""
        mock_output_handler = MagicMock()
        
        # Create a UI manager with color enabled
        ui_manager = UserInterfaceManager(
            config={"use_color": True},
            output_handler=mock_output_handler
        )
        
        # Display a message
        ui_manager.display_system_message("System is ready.")
        
        # Check that the output handler was called with the correctly formatted message
        expected_prefix = f"{ui_manager.COLORS['blue']}{ui_manager.COLORS['bold']}{ui_manager.system_prefix}{ui_manager.COLORS['reset']}"
        expected_message = f"{expected_prefix}System is ready."
        mock_output_handler.assert_called_once_with(expected_message)
    
    def test_display_system_message_without_color(self):
        """Test displaying a system message with color disabled."""
        mock_output_handler = MagicMock()
        
        # Create a UI manager with color disabled
        ui_manager = UserInterfaceManager(
            config={"use_color": False},
            output_handler=mock_output_handler
        )
        
        # Display a message
        ui_manager.display_system_message("System is ready.")
        
        # Check that the output handler was called with the correctly formatted message
        expected_message = f"{ui_manager.system_prefix}System is ready."
        mock_output_handler.assert_called_once_with(expected_message)
    
    def test_display_error_message_with_color(self):
        """Test displaying an error message with color enabled."""
        mock_output_handler = MagicMock()
        
        # Create a UI manager with color enabled
        ui_manager = UserInterfaceManager(
            config={"use_color": True},
            output_handler=mock_output_handler
        )
        
        # Display an error message
        ui_manager.display_error_message("ValidationError", "Invalid input format.")
        
        # Check that the output handler was called with the correctly formatted message
        expected_prefix = f"{ui_manager.COLORS['red']}{ui_manager.COLORS['bold']}{ui_manager.error_prefix}{ui_manager.COLORS['reset']}"
        expected_error_type = f"{ui_manager.COLORS['red']}{ui_manager.COLORS['bold']}ValidationError{ui_manager.COLORS['reset']}"
        expected_message = f"{expected_prefix}{expected_error_type}: Invalid input format."
        mock_output_handler.assert_called_once_with(expected_message)
    
    def test_display_error_message_without_color(self):
        """Test displaying an error message with color disabled."""
        mock_output_handler = MagicMock()
        
        # Create a UI manager with color disabled
        ui_manager = UserInterfaceManager(
            config={"use_color": False},
            output_handler=mock_output_handler
        )
        
        # Display an error message
        ui_manager.display_error_message("ValidationError", "Invalid input format.")
        
        # Check that the output handler was called with the correctly formatted message
        expected_message = f"{ui_manager.error_prefix}ValidationError: Invalid input format."
        mock_output_handler.assert_called_once_with(expected_message)
    
    def test_get_user_input_with_default_prompt(self):
        """Test getting user input with the default prompt."""
        mock_input_handler = MagicMock(return_value="Test user input")
        
        ui_manager = UserInterfaceManager(input_handler=mock_input_handler)
        result = ui_manager.get_user_input()
        
        # Check that the input handler was called with the default prompt
        mock_input_handler.assert_called_once_with(ui_manager.input_prompt)
        # Check that the result is correct
        assert result == "Test user input"
    
    def test_get_user_input_with_custom_prompt(self):
        """Test getting user input with a custom prompt."""
        mock_input_handler = MagicMock(return_value="Test user input")
        
        ui_manager = UserInterfaceManager(input_handler=mock_input_handler)
        result = ui_manager.get_user_input(prompt="Custom prompt: ")
        
        # Check that the input handler was called with the custom prompt
        mock_input_handler.assert_called_once_with("Custom prompt: ")
        # Check that the result is correct
        assert result == "Test user input"
    
    def test_get_multiline_input_empty_line_termination(self):
        """Test getting multi-line input terminated by an empty line."""
        # Mock input handler to return three lines followed by an empty line
        mock_input_handler = MagicMock()
        mock_input_handler.side_effect = [
            "Line 1", 
            "Line 2", 
            "Line 3", 
            ""  # Empty line terminates input
        ]
        
        mock_output_handler = MagicMock()
        
        ui_manager = UserInterfaceManager(
            input_handler=mock_input_handler,
            output_handler=mock_output_handler
        )
        
        result = ui_manager.get_multiline_input()
        
        # Check that the output handler was called with the default prompt
        expected_prompt = "Enter multiple lines (submit empty line or '<empty line>' to finish):\n"
        mock_output_handler.assert_called_once_with(expected_prompt)
        
        # Check that the input handler was called four times with empty prompt
        assert mock_input_handler.call_count == 4
        mock_input_handler.assert_has_calls([call(""), call(""), call(""), call("")])
        
        # Check that the result contains the three lines joined by newlines
        assert result == "Line 1\nLine 2\nLine 3"
    
    def test_get_multiline_input_custom_end_marker(self):
        """Test getting multi-line input terminated by a custom end marker."""
        # Mock input handler to return three lines followed by the end marker
        mock_input_handler = MagicMock()
        mock_input_handler.side_effect = [
            "Line 1", 
            "Line 2", 
            "Line 3", 
            "END"  # Custom end marker terminates input
        ]
        
        mock_output_handler = MagicMock()
        
        ui_manager = UserInterfaceManager(
            input_handler=mock_input_handler,
            output_handler=mock_output_handler
        )
        
        result = ui_manager.get_multiline_input(end_marker="END")
        
        # Check that the output handler was called with the custom prompt
        expected_prompt = "Enter multiple lines (submit empty line or 'END' to finish):\n"
        mock_output_handler.assert_called_once_with(expected_prompt)
        
        # Check that the input handler was called four times
        assert mock_input_handler.call_count == 4
        
        # Check that the result contains the three lines joined by newlines
        assert result == "Line 1\nLine 2\nLine 3"
    
    def test_get_multiline_input_custom_prompt(self):
        """Test getting multi-line input with a custom prompt."""
        # Mock input handler to return a line followed by an empty line
        mock_input_handler = MagicMock()
        mock_input_handler.side_effect = ["Line 1", ""]
        
        mock_output_handler = MagicMock()
        
        ui_manager = UserInterfaceManager(
            input_handler=mock_input_handler,
            output_handler=mock_output_handler
        )
        
        custom_prompt = "Enter your multi-line text (end with empty line):\n"
        ui_manager.get_multiline_input(prompt=custom_prompt)
        
        # Check that the output handler was called with the custom prompt
        mock_output_handler.assert_called_once_with(custom_prompt)
    
    def test_get_multiline_input_no_input(self):
        """Test getting multi-line input when no input is provided."""
        # Mock input handler to immediately return an empty line
        mock_input_handler = MagicMock(return_value="")
        
        ui_manager = UserInterfaceManager(input_handler=mock_input_handler)
        
        result = ui_manager.get_multiline_input()
        
        # Check that the result is an empty string
        assert result == ""
    
    def test_display_special_command_help_with_commands(self):
        """Test displaying help for special commands."""
        mock_output_handler = MagicMock()
        
        ui_manager = UserInterfaceManager(output_handler=mock_output_handler)
        
        commands = {
            "/help": "Display this help message",
            "/exit": "Exit the application",
            "/clear": "Clear the conversation history"
        }
        
        ui_manager.display_special_command_help(commands)
        
        # Check that the output handler was called with the correctly formatted message
        expected_help_message = "Available Commands:\n\n  /clear  - Clear the conversation history\n  /exit   - Exit the application\n  /help   - Display this help message\n"
        expected_message = ui_manager._format_system_message(expected_help_message)
        mock_output_handler.assert_called_once_with(expected_message)
    
    def test_display_special_command_help_empty_commands(self):
        """Test displaying help for special commands when no commands are provided."""
        mock_output_handler = MagicMock()
        
        ui_manager = UserInterfaceManager(output_handler=mock_output_handler)
        
        ui_manager.display_special_command_help({})
        
        # Check that the output handler was not called
        mock_output_handler.assert_not_called()
    
    def test_default_input_handler_normal(self):
        """Test the default input handler under normal conditions."""
        with patch('builtins.input', return_value="Test input"):
            ui_manager = UserInterfaceManager()
            result = ui_manager._default_input_handler("Prompt: ")
            
            # Check that the result is the expected input
            assert result == "Test input"
    
    def test_default_input_handler_eof_error(self):
        """Test the default input handler when EOFError is raised."""
        with patch('builtins.input', side_effect=EOFError), patch('builtins.print') as mock_print:
            ui_manager = UserInterfaceManager()
            result = ui_manager._default_input_handler("Prompt: ")
            
            # Check that print was called (to add a newline)
            mock_print.assert_called_once_with()
            # Check that an empty string is returned
            assert result == ""
    
    def test_default_input_handler_keyboard_interrupt(self):
        """Test the default input handler when KeyboardInterrupt is raised."""
        with patch('builtins.input', side_effect=KeyboardInterrupt), patch('builtins.print') as mock_print:
            ui_manager = UserInterfaceManager()
            result = ui_manager._default_input_handler("Prompt: ")
            
            # Check that print was called (to add a newline)
            mock_print.assert_called_once_with()
            # Check that an empty string is returned
            assert result == ""
    
    def test_default_output_handler(self):
        """Test the default output handler."""
        with patch('builtins.print') as mock_print:
            ui_manager = UserInterfaceManager()
            ui_manager._default_output_handler("Test message")
            
            # Check that print was called with the message
            mock_print.assert_called_once_with("Test message")
    
    def test_supports_color_no_color_env_var(self):
        """Test color support detection when NO_COLOR environment variable is set."""
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # NO_COLOR being set should return False
            assert result is False
    
    def test_supports_color_not_a_tty(self):
        """Test color support detection when stdout is not a TTY."""
        with patch.object(sys.stdout, 'isatty', return_value=False):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Not a TTY should return False
            assert result is False
    
    def test_supports_color_windows_with_ansicon(self):
        """Test color support detection on Windows with ANSICON environment variable."""
        with patch.dict(os.environ, {"ANSICON": "1"}), \
             patch('sys.platform', 'win32'), \
             patch.object(sys.stdout, 'isatty', return_value=True):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Windows with ANSICON should return True
            assert result is True
    
    def test_supports_color_windows_with_wt_session(self):
        """Test color support detection on Windows with WT_SESSION environment variable."""
        with patch.dict(os.environ, {"WT_SESSION": "1"}), \
             patch('sys.platform', 'win32'), \
             patch.object(sys.stdout, 'isatty', return_value=True):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Windows with WT_SESSION should return True
            assert result is True
    
    def test_supports_color_windows_with_conemu(self):
        """Test color support detection on Windows with ConEmuANSI environment variable."""
        with patch.dict(os.environ, {"ConEmuANSI": "1"}), \
             patch('sys.platform', 'win32'), \
             patch.object(sys.stdout, 'isatty', return_value=True):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Windows with ConEmuANSI should return True
            assert result is True
    
    def test_supports_color_windows_with_vscode(self):
        """Test color support detection on Windows with VSCode terminal."""
        with patch.dict(os.environ, {"TERM_PROGRAM": "vscode"}), \
             patch('sys.platform', 'win32'), \
             patch.object(sys.stdout, 'isatty', return_value=True):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Windows in VSCode terminal should return True
            assert result is True
    
    def test_supports_color_windows_without_env_vars(self):
        """Test color support detection on Windows without special environment variables."""
        with patch.dict(os.environ, clear=True), \
             patch('sys.platform', 'win32'), \
             patch.object(sys.stdout, 'isatty', return_value=True):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Windows without special env vars should return False
            assert result is False
    
    def test_supports_color_unix_with_valid_term(self):
        """Test color support detection on Unix-like platforms with valid TERM value."""
        with patch.dict(os.environ, {"TERM": "xterm-256color"}), \
             patch('sys.platform', 'linux'), \
             patch.object(sys.stdout, 'isatty', return_value=True):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Unix with valid TERM should return True
            assert result is True
    
    def test_supports_color_unix_with_invalid_term(self):
        """Test color support detection on Unix-like platforms with invalid TERM value."""
        with patch.dict(os.environ, {"TERM": "dumb"}), \
             patch('sys.platform', 'linux'), \
             patch.object(sys.stdout, 'isatty', return_value=True):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Unix with TERM=dumb should return False
            assert result is False
    
    def test_supports_color_unix_without_term(self):
        """Test color support detection on Unix-like platforms without TERM environment variable."""
        with patch.dict(os.environ, clear=True), \
             patch('sys.platform', 'darwin'), \
             patch.object(sys.stdout, 'isatty', return_value=True):
            ui_manager = UserInterfaceManager()
            result = ui_manager._supports_color()
            
            # Unix without TERM should return False
            assert result is False