"""
Unit tests for the TEPSManager class.

This module tests the functionality of the TEPSManager class
located in framework_core/component_managers/teps_manager.py.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, ANY

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from framework_core.component_managers.teps_manager import TEPSManager
from framework_core.exceptions import TEPSInitError


class TestTEPSManager:
    """Test suite for the TEPSManager class."""
    
    @pytest.fixture
    def teps_settings(self):
        """Create sample TEPS settings."""
        return {
            "dry_run_enabled": True,
            "bash": {
                "allowed_commands": ["ls", "echo", "cat"],
                "blocked_commands": ["rm", "sudo", "chmod"]
            }
        }
    
    @pytest.fixture
    def tool_request(self):
        """Create a sample tool request."""
        return {
            "request_id": "test-123",
            "tool_name": "executeBashCommand",
            "parameters": {
                "command": "echo 'Hello World'"
            },
            "icerc_full_text": "Intent: Display text\nCommand: echo command\nExpected Outcome: Text displayed\nRisk: Low"
        }
    
    def test_init_with_settings(self, teps_settings):
        """Test initialization with settings."""
        # Mock the logger
        with patch('framework_core.component_managers.teps_manager.setup_logger'):
            manager = TEPSManager(teps_settings)
            
            assert manager.teps_settings == teps_settings
            assert manager.teps_instance is None
    
    def test_init_without_settings(self):
        """Test initialization without settings."""
        # Mock the logger
        with patch('framework_core.component_managers.teps_manager.setup_logger'):
            manager = TEPSManager()
            
            assert manager.teps_settings == {}
            assert manager.teps_instance is None
    
    def test_initialize_success(self, teps_settings):
        """Test successful initialization of the TEPS component."""
        # Setup
        mock_logger = MagicMock()
        mock_teps_instance = MagicMock()
        
        # Create a real TEPS instance for the test
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger), \
             patch('framework_core.component_managers.teps_manager.TEPSEngine', return_value=mock_teps_instance):
            
            # Create manager and initialize
            manager = TEPSManager(teps_settings)
            manager.initialize()
            
            # Assertions
            assert manager.teps_instance is mock_teps_instance
            assert mock_logger.info.call_count >= 2  # At least two info logs
    
    def test_initialize_exception(self, teps_settings):
        """Test initialization handling exceptions."""
        # Setup
        mock_logger = MagicMock()
        
        # Mock the logger setup and TEPS class to raise an exception
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger), \
             patch('framework_core.component_managers.teps_manager.TEPSEngine', side_effect=Exception("TEPS initialization failed")):
            
            # Create manager
            manager = TEPSManager(teps_settings)
            
            # Act & Assert
            with pytest.raises(TEPSInitError, match="Failed to initialize TEPS: TEPS initialization failed"):
                manager.initialize()
            
            # Assert the logger recorded the error
            assert mock_logger.error.call_count >= 1
    
    def test_execute_tool_success(self, teps_settings, tool_request):
        """Test successful execution of a tool."""
        # Setup
        mock_logger = MagicMock()
        mock_teps_instance = MagicMock()
        expected_result = {
            "request_id": "test-123",
            "tool_name": "executeBashCommand",
            "status": "success",
            "data": {
                "stdout": "Hello World",
                "stderr": "",
                "exit_code": 0
            }
        }
        mock_teps_instance.execute_tool.return_value = expected_result
        
        # Create manager with mocked dependencies
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger):
            manager = TEPSManager(teps_settings)
            manager.teps_instance = mock_teps_instance
            
            # Act
            result = manager.execute_tool(tool_request)
            
            # Assert
            assert result == expected_result
            mock_teps_instance.execute_tool.assert_called_once_with(tool_request)
            # Check if info was logged (using 'in' since we don't care about the exact format)
            assert mock_logger.info.call_count >= 1
    
    def test_execute_tool_not_initialized(self, tool_request):
        """Test execute_tool when TEPS is not initialized."""
        # Setup
        mock_logger = MagicMock()
        
        # Create manager with mocked logger
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger):
            manager = TEPSManager()
            manager.teps_instance = None
            
            # Act & Assert
            with pytest.raises(TEPSInitError, match="TEPS not initialized"):
                manager.execute_tool(tool_request)
            
            # Assert the logger recorded the error
            mock_logger.error.assert_called_once()
    
    def test_execute_tool_error(self, teps_settings, tool_request):
        """Test execute_tool handling a TEPS execution error."""
        # Setup
        mock_logger = MagicMock()
        mock_teps_instance = MagicMock()
        error_result = {
            "request_id": "test-123",
            "tool_name": "executeBashCommand",
            "status": "error",
            "data": {
                "error_message": "Command execution failed"
            }
        }
        mock_teps_instance.execute_tool.return_value = error_result
        
        # Create manager with mocked dependencies
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger):
            manager = TEPSManager(teps_settings)
            manager.teps_instance = mock_teps_instance
            
            # Act
            result = manager.execute_tool(tool_request)
            
            # Assert
            assert result == error_result
            mock_teps_instance.execute_tool.assert_called_once_with(tool_request)
            # Check if info was logged
            assert mock_logger.info.call_count >= 1
    
    def test_execute_tool_declined(self, teps_settings, tool_request):
        """Test execute_tool handling user declining execution."""
        # Setup
        mock_logger = MagicMock()
        mock_teps_instance = MagicMock()
        declined_result = {
            "request_id": "test-123",
            "tool_name": "executeBashCommand",
            "status": "declined_by_user",
            "data": {
                "message": "User declined execution."
            }
        }
        mock_teps_instance.execute_tool.return_value = declined_result
        
        # Create manager with mocked dependencies
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger):
            manager = TEPSManager(teps_settings)
            manager.teps_instance = mock_teps_instance
            
            # Act
            result = manager.execute_tool(tool_request)
            
            # Assert
            assert result == declined_result
            mock_teps_instance.execute_tool.assert_called_once_with(tool_request)
            # Check if info was logged
            assert mock_logger.info.call_count >= 1
    
    def test_execute_tool_with_project_root(self, teps_settings, tool_request):
        """Test execute_tool with a specified project root path."""
        # Setup
        mock_logger = MagicMock()
        mock_teps_instance = MagicMock()
        expected_result = {
            "request_id": "test-123",
            "tool_name": "executeBashCommand",
            "status": "success",
            "data": {
                "stdout": "Hello World",
                "stderr": "",
                "exit_code": 0
            }
        }
        mock_teps_instance.execute_tool.return_value = expected_result
        
        # Create manager with mocked dependencies and project root path
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger):
            manager = TEPSManager(teps_settings)
            manager.teps_instance = mock_teps_instance
            
            # Add project_root_path to settings
            manager.teps_settings["project_root_path"] = "/project/root"
            
            # Act
            result = manager.execute_tool(tool_request)
            
            # Assert
            assert result == expected_result
            mock_teps_instance.execute_tool.assert_called_once_with(tool_request)
            assert mock_logger.info.call_count >= 1
    
    def test_initialize_with_project_root_path(self, teps_settings):
        """Test initialize with project_root_path in settings."""
        # Setup
        mock_logger = MagicMock()
        mock_teps_instance = MagicMock()
        teps_settings_with_root = teps_settings.copy()
        teps_settings_with_root["project_root_path"] = "/project/root"
        
        # Mock dependencies - make sure to patch the correct import path in the teps_manager module
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger), \
             patch('framework_core.component_managers.teps_manager.TEPSEngine', return_value=mock_teps_instance):
            
            # Create manager and initialize
            manager = TEPSManager(teps_settings_with_root)
            manager.initialize()
            
            # Assertions
            assert manager.teps_instance is mock_teps_instance
            assert mock_logger.info.call_count >= 2
    
    def test_execute_multiple_tools(self, teps_settings):
        """Test executing multiple tools in sequence."""
        # Setup
        mock_logger = MagicMock()
        mock_teps_instance = MagicMock()
        
        # Create two different tool requests
        bash_request = {
            "request_id": "bash-123",
            "tool_name": "executeBashCommand",
            "parameters": {"command": "ls"},
            "icerc_full_text": "Intent: List files\nCommand: ls\nExpected: File list\nRisk: Low"
        }
        
        read_request = {
            "request_id": "read-456",
            "tool_name": "readFile",
            "parameters": {"file_path": "/path/to/file.txt"},
            "icerc_full_text": "Intent: Read file\nCommand: Read file\nExpected: File content\nRisk: Low"
        }
        
        # Configure mock responses
        bash_result = {
            "request_id": "bash-123",
            "tool_name": "executeBashCommand", 
            "status": "success",
            "data": {"stdout": "file1.txt file2.txt", "stderr": "", "exit_code": 0}
        }
        
        read_result = {
            "request_id": "read-456",
            "tool_name": "readFile",
            "status": "success",
            "data": {"file_path": "/path/to/file.txt", "content": "Hello World"}
        }
        
        mock_teps_instance.execute_tool.side_effect = [bash_result, read_result]
        
        # Create manager
        with patch('framework_core.component_managers.teps_manager.setup_logger', return_value=mock_logger):
            manager = TEPSManager(teps_settings)
            manager.teps_instance = mock_teps_instance
            
            # Execute the tools
            result1 = manager.execute_tool(bash_request)
            result2 = manager.execute_tool(read_request)
            
            # Assert
            assert result1 == bash_result
            assert result2 == read_result
            assert mock_teps_instance.execute_tool.call_count == 2
            mock_teps_instance.execute_tool.assert_any_call(bash_request)
            mock_teps_instance.execute_tool.assert_any_call(read_request)
            assert mock_logger.info.call_count >= 2  # At least one log per execution