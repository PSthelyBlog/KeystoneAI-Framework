"""
User interface management for the Framework Core Application.

This module handles user input and output formatting.
"""

import sys
import os
import re
from typing import Callable, Optional, Dict, Any, List

from framework_core.utils.logging_utils import setup_logger

class UserInterfaceManager:
    """
    Manages user interface interactions, including input/output and formatting.
    """
    
    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "gray": "\033[90m"
    }
    
    def __init__(
        self, 
        config: Optional[Dict[str, Any]] = None,
        input_handler: Optional[Callable[[str], str]] = None,
        output_handler: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the User Interface Manager.
        
        Args:
            config: Optional configuration dictionary
            input_handler: Optional custom input handler function
            output_handler: Optional custom output handler function
        """
        self.logger = setup_logger("ui_manager")
        self.config = config or {}
        self.input_handler = input_handler or self._default_input_handler
        self.output_handler = output_handler or self._default_output_handler
        
        # Configure from config dict
        self.input_prompt = self.config.get("input_prompt", "> ")
        self.assistant_prefix = self.config.get("assistant_prefix", "(AI): ")
        self.system_prefix = self.config.get("system_prefix", "[System]: ")
        self.error_prefix = self.config.get("error_prefix", "[Error]: ")
        
        # Check if color is supported and enabled
        self.use_color = self.config.get("use_color", self._supports_color())
        
    def display_assistant_message(self, message: str) -> None:
        """
        Display an assistant message to the user.
        
        Args:
            message: The message to display
        """
        formatted_message = self._format_assistant_message(message)
        self.output_handler(formatted_message)
        
    def set_assistant_prefix(self, prefix: str) -> None:
        """
        Set a new assistant prefix for message display.
        
        Args:
            prefix: The new prefix to use for assistant messages
        """
        self.assistant_prefix = prefix
        self.logger.debug(f"Assistant prefix updated to: {prefix}")
        
    def display_system_message(self, message: str) -> None:
        """
        Display a system message to the user.
        
        Args:
            message: The message to display
        """
        formatted_message = self._format_system_message(message)
        self.output_handler(formatted_message)
        
    def display_error_message(self, error_type: str, error_message: str) -> None:
        """
        Display an error message to the user.
        
        Args:
            error_type: The type of error
            error_message: The error message
        """
        formatted_message = self._format_error_message(error_type, error_message)
        self.output_handler(formatted_message)
        
    def get_user_input(self, prompt: Optional[str] = None) -> str:
        """
        Get input from the user.
        
        Args:
            prompt: Optional custom prompt
            
        Returns:
            User input string
        """
        prompt = prompt or self.input_prompt
        return self.input_handler(prompt)
        
    def get_multiline_input(
        self, 
        prompt: Optional[str] = None, 
        end_marker: str = ""
    ) -> str:
        """
        Get multi-line input from the user.
        
        Args:
            prompt: Optional custom prompt
            end_marker: String that marks the end of input
            
        Returns:
            Multi-line user input
        """
        prompt = prompt or "Enter multiple lines (submit empty line or '{end}' to finish):\n".format(
            end=end_marker or "<empty line>"
        )
        
        self.output_handler(prompt)
        
        lines = []
        while True:
            line = self.input_handler("")
            
            if (not line and not end_marker) or line == end_marker:
                break
                
            lines.append(line)
            
        return "\n".join(lines)
        
    def display_special_command_help(self, commands: Dict[str, str]) -> None:
        """
        Display help for special commands.
        
        Args:
            commands: Dictionary mapping command names to descriptions
        """
        if not commands:
            return
            
        help_message = "Available Commands:\n\n"
        
        max_len = max(len(cmd) for cmd in commands.keys())
        
        for cmd, desc in sorted(commands.items()):
            help_message += f"  {cmd.ljust(max_len)}  - {desc}\n"
            
        formatted_message = self._format_system_message(help_message)
        self.output_handler(formatted_message)
        
    def _format_assistant_message(self, message: str) -> str:
        """
        Format an assistant message for display.
        
        Args:
            message: The message to format
            
        Returns:
            Formatted message
        """
        if self.use_color:
            prefix = f"{self.COLORS['green']}{self.COLORS['bold']}{self.assistant_prefix}{self.COLORS['reset']}"
        else:
            prefix = self.assistant_prefix
            
        return f"{prefix}{message}"
        
    def _format_system_message(self, message: str) -> str:
        """
        Format a system message for display.
        
        Args:
            message: The message to format
            
        Returns:
            Formatted message
        """
        if self.use_color:
            prefix = f"{self.COLORS['blue']}{self.COLORS['bold']}{self.system_prefix}{self.COLORS['reset']}"
        else:
            prefix = self.system_prefix
            
        return f"{prefix}{message}"
        
    def _format_error_message(self, error_type: str, error_message: str) -> str:
        """
        Format an error message for display.
        
        Args:
            error_type: The type of error
            error_message: The error message
            
        Returns:
            Formatted message
        """
        if self.use_color:
            prefix = f"{self.COLORS['red']}{self.COLORS['bold']}{self.error_prefix}{self.COLORS['reset']}"
            error_type_str = f"{self.COLORS['red']}{self.COLORS['bold']}{error_type}{self.COLORS['reset']}"
        else:
            prefix = self.error_prefix
            error_type_str = error_type
            
        return f"{prefix}{error_type_str}: {error_message}"
        
    def _default_input_handler(self, prompt: str) -> str:
        """
        Default input handler implementation.
        
        Args:
            prompt: Input prompt
            
        Returns:
            User input
        """
        try:
            return input(prompt)
        except EOFError:
            # Handle Ctrl+D gracefully
            print()  # Add newline
            return ""
        except KeyboardInterrupt:
            # Handle Ctrl+C by returning empty string
            print()  # Add newline
            return ""
        
    def _default_output_handler(self, message: str) -> None:
        """
        Default output handler implementation.
        
        Args:
            message: Message to output
        """
        print(message)
        
    def _supports_color(self) -> bool:
        """
        Check if the terminal supports color output.
        
        Returns:
            True if color is supported, False otherwise
        """
        # Check if NO_COLOR environment variable is set
        if os.environ.get("NO_COLOR") is not None:
            return False
            
        # Check if output is a TTY
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False
            
        # Check platform-specific color support
        platform = sys.platform.lower()
        if platform == "win32":
            # On Windows, check for ANSICON or ConEMU or Windows Terminal
            return (
                "ANSICON" in os.environ
                or "WT_SESSION" in os.environ
                or "ConEmuANSI" in os.environ
                or os.environ.get("TERM_PROGRAM") == "vscode"
            )
        else:
            # On Unix-like platforms, check TERM environment variable
            return os.environ.get("TERM") not in (None, "", "dumb")