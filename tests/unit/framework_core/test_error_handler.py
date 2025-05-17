"""
Unit tests for the ErrorHandler class.

This module tests all the functionality of the ErrorHandler class
located in framework_core/error_handler.py.
"""

import pytest
import traceback
from unittest.mock import patch, MagicMock, call

from framework_core.error_handler import ErrorHandler


class TestErrorHandler:
    """Test suite for the ErrorHandler class."""
    
    def test_init(self):
        """Test initialization of ErrorHandler."""
        # Patch the setup_logger to verify it's called correctly
        with patch('framework_core.error_handler.setup_logger') as mock_setup_logger:
            # Create mock logger to be returned by setup_logger
            mock_logger = MagicMock()
            mock_setup_logger.return_value = mock_logger
            
            # Initialize ErrorHandler
            error_handler = ErrorHandler()
            
            # Verify setup_logger was called with correct name
            mock_setup_logger.assert_called_once_with("error_handler")
            
            # Verify logger is correctly assigned
            assert error_handler.logger == mock_logger
    
    def test_handle_error_without_exception(self):
        """Test handle_error method without an exception object."""
        # Create error handler with mock logger
        error_handler = ErrorHandler()
        error_handler.logger = MagicMock()
        
        # Test data
        error_type = "ValidationError"
        error_message = "Invalid input format"
        
        # Call handle_error
        result = error_handler.handle_error(error_type, error_message)
        
        # Verify logger was called correctly
        error_handler.logger.error.assert_called_once_with(f"{error_type}: {error_message}")
        
        # Verify return value is the error message
        assert result == error_message
    
    def test_handle_error_with_exception(self):
        """Test handle_error method with an exception object."""
        # Create error handler with mock logger
        error_handler = ErrorHandler()
        error_handler.logger = MagicMock()
        
        # Test data
        error_type = "RuntimeError"
        error_message = "An unexpected error occurred"
        test_exception = ValueError("Test exception")
        
        # Mock traceback.format_exc to return a known string
        expected_traceback = "Traceback (most recent call last):\n  ...\nValueError: Test exception"
        with patch('traceback.format_exc', return_value=expected_traceback):
            # Call handle_error
            result = error_handler.handle_error(error_type, error_message, test_exception)
        
        # Verify logger was called correctly with exception details
        expected_log_message = (
            f"{error_type}: {error_message}\n"
            f"Exception: {str(test_exception)}\n"
            f"{expected_traceback}"
        )
        error_handler.logger.error.assert_called_once_with(expected_log_message)
        
        # Verify return value is the error message
        assert result == error_message
    
    def test_handle_error_with_context(self):
        """Test handle_error method with context information."""
        # Create error handler with mock logger
        error_handler = ErrorHandler()
        error_handler.logger = MagicMock()
        
        # Test data
        error_type = "ConfigError"
        error_message = "Configuration file not found"
        context = {
            "file_path": "/path/to/config.yaml",
            "attempted_actions": ["search", "create_default"]
        }
        
        # Call handle_error
        result = error_handler.handle_error(error_type, error_message, context=context)
        
        # Verify logger was called correctly for both error and context
        error_handler.logger.error.assert_has_calls([
            call(f"{error_type}: {error_message}"),
            call(f"Error context: {context}")
        ])
        
        # Verify return value is the error message
        assert result == error_message
    
    def test_handle_error_with_exception_and_context(self):
        """Test handle_error method with both exception and context."""
        # Create error handler with mock logger
        error_handler = ErrorHandler()
        error_handler.logger = MagicMock()
        
        # Test data
        error_type = "APIError"
        error_message = "Failed to connect to external API"
        test_exception = ConnectionError("Connection timeout")
        context = {
            "api_endpoint": "https://api.example.com/data",
            "timeout": 30,
            "retry_attempts": 3
        }
        
        # Mock traceback.format_exc to return a known string
        expected_traceback = "Traceback (most recent call last):\n  ...\nConnectionError: Connection timeout"
        with patch('traceback.format_exc', return_value=expected_traceback):
            # Call handle_error
            result = error_handler.handle_error(
                error_type, 
                error_message, 
                test_exception, 
                context
            )
        
        # Verify logger was called correctly with exception details and context
        expected_log_message = (
            f"{error_type}: {error_message}\n"
            f"Exception: {str(test_exception)}\n"
            f"{expected_traceback}"
        )
        error_handler.logger.error.assert_has_calls([
            call(expected_log_message),
            call(f"Error context: {context}")
        ])
        
        # Verify return value is the error message
        assert result == error_message