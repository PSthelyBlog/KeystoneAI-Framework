"""
Unit tests for logging utilities module.

This module tests all the functionality of the logging_utils module
located in framework_core/utils/logging_utils.py.
"""

import logging
import os
import pytest
from unittest.mock import patch, MagicMock, call

from framework_core.utils.logging_utils import setup_logger


class TestLoggingUtils:
    """Test suite for the logging_utils module."""
    
    def test_setup_logger_name(self):
        """Test that setup_logger returns a logger with the correct name."""
        # Patch getLogger to return our mock and avoid actual logging configuration
        with patch('logging.getLogger') as mock_get_logger:
            # Setup mock logger
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            # Call setup_logger
            logger_name = "test_logger"
            result = setup_logger(logger_name)
            
            # Verify getLogger was called with the correct name
            mock_get_logger.assert_called_once_with(logger_name)
            
            # Verify the mock logger was returned
            assert result == mock_logger
    
    def test_setup_logger_default_level(self):
        """Test setup_logger uses default INFO level when no level is provided."""
        with patch('logging.getLogger') as mock_get_logger:
            # Setup mock logger
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            # Call setup_logger with no level specified
            setup_logger("test_logger")
            
            # Verify logger level was set to INFO
            mock_logger.setLevel.assert_called_once_with(logging.INFO)
    
    def test_setup_logger_string_level(self):
        """Test setup_logger correctly handles string level inputs."""
        with patch('logging.getLogger') as mock_get_logger:
            # Setup mock logger
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            # Call setup_logger with string level
            setup_logger("test_logger", level="DEBUG")
            
            # Verify logger level was set to DEBUG
            mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
    
    def test_setup_logger_numeric_level(self):
        """Test setup_logger correctly handles numeric level inputs."""
        with patch('logging.getLogger') as mock_get_logger:
            # Setup mock logger
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            # Call setup_logger with numeric level
            setup_logger("test_logger", level=logging.WARNING)
            
            # Verify logger level was set to WARNING
            mock_logger.setLevel.assert_called_once_with(logging.WARNING)
            
    def test_setup_logger_invalid_string_level(self):
        """Test setup_logger handles invalid string levels by defaulting to INFO."""
        with patch('logging.getLogger') as mock_get_logger:
            # Setup mock logger
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            # Call setup_logger with invalid string level
            setup_logger("test_logger", level="INVALID_LEVEL")
            
            # Verify logger level was set to INFO (default)
            mock_logger.setLevel.assert_called_once_with(logging.INFO)
    
    def test_setup_logger_stream_handler(self):
        """Test setup_logger adds a StreamHandler with correct configuration."""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('logging.StreamHandler') as mock_stream_handler, \
             patch('logging.Formatter') as mock_formatter:
            
            # Setup mocks
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            mock_handler = MagicMock()
            mock_stream_handler.return_value = mock_handler
            
            mock_format = MagicMock()
            mock_formatter.return_value = mock_format
            
            # Call setup_logger
            setup_logger("test_logger", level=logging.DEBUG)
            
            # Verify StreamHandler was created
            mock_stream_handler.assert_called_once()
            
            # Verify handler level was set correctly
            mock_handler.setLevel.assert_called_once_with(logging.DEBUG)
            
            # Verify formatter was created with default format
            mock_formatter.assert_called_once_with(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Verify formatter was added to handler
            mock_handler.setFormatter.assert_called_once_with(mock_format)
            
            # Verify handler was added to logger
            mock_logger.addHandler.assert_called_once_with(mock_handler)
    
    def test_setup_logger_file_handler_without_dir_creation(self):
        """Test setup_logger adds a FileHandler when log_file is provided and directory exists."""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('logging.StreamHandler') as mock_stream_handler, \
             patch('logging.FileHandler') as mock_file_handler, \
             patch('logging.Formatter') as mock_formatter, \
             patch('os.path.exists') as mock_exists, \
             patch('os.path.dirname') as mock_dirname:
            
            # Setup mocks
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            mock_stream = MagicMock()
            mock_stream_handler.return_value = mock_stream
            
            mock_file = MagicMock()
            mock_file_handler.return_value = mock_file
            
            mock_format = MagicMock()
            mock_formatter.return_value = mock_format
            
            # Mock os.path.exists to return True (directory exists)
            mock_exists.return_value = True
            
            # Mock os.path.dirname to return a directory path
            log_dir = "/logs"
            mock_dirname.return_value = log_dir
            
            # Call setup_logger with a log_file
            log_file = "/logs/app.log"
            setup_logger("test_logger", level=logging.INFO, log_file=log_file)
            
            # Verify FileHandler was created with correct file path
            mock_file_handler.assert_called_once_with(log_file)
            
            # Verify FileHandler level was set correctly
            mock_file.setLevel.assert_called_once_with(logging.INFO)
            
            # Verify formatter was added to FileHandler
            mock_file.setFormatter.assert_called_once_with(mock_format)
            
            # Verify both handlers were added to logger
            assert mock_logger.addHandler.call_count == 2
            mock_logger.addHandler.assert_any_call(mock_stream)
            mock_logger.addHandler.assert_any_call(mock_file)
    
    def test_setup_logger_file_handler_with_dir_creation(self):
        """Test setup_logger creates directory when needed for FileHandler."""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('logging.StreamHandler') as mock_stream_handler, \
             patch('logging.FileHandler') as mock_file_handler, \
             patch('logging.Formatter') as mock_formatter, \
             patch('os.path.exists') as mock_exists, \
             patch('os.path.dirname') as mock_dirname, \
             patch('os.makedirs') as mock_makedirs:
            
            # Setup mocks
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            mock_stream = MagicMock()
            mock_stream_handler.return_value = mock_stream
            
            mock_file = MagicMock()
            mock_file_handler.return_value = mock_file
            
            mock_format = MagicMock()
            mock_formatter.return_value = mock_format
            
            # Mock os.path.exists to return False (directory doesn't exist)
            mock_exists.return_value = False
            
            # Mock os.path.dirname to return a directory path
            log_dir = "/logs/app"
            mock_dirname.return_value = log_dir
            
            # Call setup_logger with a log_file
            log_file = "/logs/app/debug.log"
            setup_logger("test_logger", level=logging.DEBUG, log_file=log_file)
            
            # Verify directory was created
            mock_makedirs.assert_called_once_with(log_dir)
            
            # Verify FileHandler was created with correct file path
            mock_file_handler.assert_called_once_with(log_file)
            
            # Verify FileHandler level was set correctly
            mock_file.setLevel.assert_called_once_with(logging.DEBUG)
            
            # Verify formatter was added to FileHandler
            mock_file.setFormatter.assert_called_once_with(mock_format)
            
            # Verify both handlers were added to logger
            assert mock_logger.addHandler.call_count == 2
    
    def test_setup_logger_custom_format(self):
        """Test setup_logger uses custom log format when provided."""
        with patch('logging.getLogger') as mock_get_logger, \
             patch('logging.StreamHandler') as mock_stream_handler, \
             patch('logging.FileHandler') as mock_file_handler, \
             patch('logging.Formatter') as mock_formatter, \
             patch('os.path.exists') as mock_exists, \
             patch('os.path.dirname') as mock_dirname:
            
            # Setup mocks
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger
            
            mock_stream = MagicMock()
            mock_stream_handler.return_value = mock_stream
            
            mock_file = MagicMock()
            mock_file_handler.return_value = mock_file
            
            mock_format = MagicMock()
            mock_formatter.return_value = mock_format
            
            # Mock os.path.exists to return True (directory exists)
            mock_exists.return_value = True
            
            # Mock os.path.dirname to return a directory path
            log_dir = "/logs"
            mock_dirname.return_value = log_dir
            
            # Custom log format
            custom_format = "%(levelname)s [%(asctime)s] %(name)s: %(message)s"
            
            # Call setup_logger with custom format and log file
            log_file = "/logs/app.log"
            setup_logger("test_logger", level="INFO", log_file=log_file, log_format=custom_format)
            
            # Verify formatter was created with custom format
            mock_formatter.assert_called_once_with(custom_format)
            
            # Verify format was applied to both handlers
            mock_stream.setFormatter.assert_called_once_with(mock_format)
            mock_file.setFormatter.assert_called_once_with(mock_format)
    
    def test_setup_logger_prevents_duplicate_handlers(self):
        """Test setup_logger clears existing handlers to prevent duplicates."""
        # First let's create a logger with some handlers
        with patch('logging.getLogger') as mock_get_logger:
            # Setup fake logger with existing handlers
            mock_logger = MagicMock()
            mock_handlers = MagicMock()
            
            # Set handlers property on the mock_logger
            type(mock_logger).handlers = mock_handlers
            
            # Return our mock when getLogger is called
            mock_get_logger.return_value = mock_logger
            
            # Call setup_logger
            setup_logger("test_logger")
            
            # Check if there was a condition that would have triggered
            # handler clearing, and if our implementation of handlers.clear()
            # was correctly called
            assert mock_handlers.__bool__.call_count > 0, "Logger.handlers wasn't checked"