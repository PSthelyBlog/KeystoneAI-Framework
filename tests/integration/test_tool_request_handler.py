"""
Integration tests for the ToolRequestHandler component.

These tests verify the ToolRequestHandler's ability to process tool requests,
interact with the TEPS component, and format results for message history.
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.tool_request_handler import ToolRequestHandler
from framework_core.exceptions import ToolExecutionError
from tests.integration.utils import IntegrationTestCase


class TestToolRequestHandlerIntegration(IntegrationTestCase):
    """
    Integration tests for the ToolRequestHandler component.
    
    These tests validate that:
    1. Tool requests are processed correctly
    2. Interaction with TEPS component works as expected
    3. Error handling is robust
    4. Tool result formatting is appropriate for message history
    5. Batch processing functions correctly
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        super().setup_method()
        
        # Create a mock TEPS instance
        self.teps_instance = MagicMock(name="TEPSEngine")
        
        # Create a mock TEPS manager
        self.teps_manager = MagicMock(name="TEPSManager")
        self.teps_manager.teps_instance = self.teps_instance
        
        # Configure the execute_tool method
        def mock_execute_tool(tool_request):
            tool_name = tool_request.get("tool_name", "unknown")
            request_id = tool_request.get("request_id", "req-123")
            params = tool_request.get("parameters", {})
            
            # Handle different tools appropriately
            if tool_name == "readFile":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": f"Content of file at {params.get('file_path', 'unknown_path')}"
                }
            elif tool_name == "writeFile":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": {
                        "bytes_written": len(params.get("content", "")),
                        "path": params.get("file_path", "unknown_path")
                    }
                }
            elif tool_name == "executeBashCommand":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": f"Output of command: {params.get('command', 'unknown_command')}"
                }
            elif tool_name == "errorTool":
                # Simulate failure
                raise ValueError("Simulated tool error")
            elif tool_name == "validationErrorTool":
                # This will trigger validation error (missing required fields)
                return {}
            else:
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": {"message": "Generic tool executed successfully"}
                }
        
        # Assign the mock side_effect to the Mock's execute_tool method
        self.teps_manager.execute_tool.side_effect = mock_execute_tool
        
        # Create the ToolRequestHandler
        self.tool_request_handler = ToolRequestHandler(teps_manager=self.teps_manager)
        
        # Prepare sample tool requests for testing
        self.read_file_request = {
            "request_id": "read-123",
            "tool_name": "readFile",
            "parameters": {"file_path": "/path/to/file.txt"},
            "icerc_full_text": "Intent: Read file\nCommand: Read file at /path/to/file.txt\nExpected: File content\nRisk: Low\nConfirmation: [Y/N]"
        }
        
        self.write_file_request = {
            "request_id": "write-456",
            "tool_name": "writeFile",
            "parameters": {"file_path": "/path/to/output.txt", "content": "Test content"},
            "icerc_full_text": "Intent: Write file\nCommand: Write to /path/to/output.txt\nExpected: File created\nRisk: Medium\nConfirmation: [Y/N]"
        }
        
        self.bash_command_request = {
            "request_id": "bash-789",
            "tool_name": "executeBashCommand",
            "parameters": {"command": "ls -la"},
            "icerc_full_text": "Intent: List files\nCommand: ls -la\nExpected: Directory listing\nRisk: Low\nConfirmation: [Y/N]"
        }
        
        self.error_tool_request = {
            "request_id": "error-999",
            "tool_name": "errorTool",
            "parameters": {"param": "value"},
            "icerc_full_text": "Intent: Trigger error\nCommand: errorTool\nExpected: Error\nRisk: None\nConfirmation: [Y/N]"
        }
        
        self.invalid_request = {
            "request_id": "invalid-000",
            "tool_name": "readFile",
            # Missing parameters
            "icerc_full_text": "Intent: Invalid request\nCommand: None\nExpected: Error\nRisk: None\nConfirmation: [Y/N]"
        }
    
    def test_process_read_file_request(self):
        """Test processing a readFile tool request."""
        # Process the request
        result = self.tool_request_handler.process_tool_request(self.read_file_request)
        
        # Verify the result
        assert isinstance(result, dict)
        assert result["request_id"] == "read-123"
        assert result["tool_name"] == "readFile"
        assert result["status"] == "success"
        assert "Content of file at /path/to/file.txt" in result["data"]
        
        # Verify TEPS was called with the correct request
        self.teps_manager.execute_tool.assert_called_once_with(self.read_file_request)
    
    def test_process_write_file_request(self):
        """Test processing a writeFile tool request."""
        # Process the request
        result = self.tool_request_handler.process_tool_request(self.write_file_request)
        
        # Verify the result
        assert isinstance(result, dict)
        assert result["request_id"] == "write-456"
        assert result["tool_name"] == "writeFile"
        assert result["status"] == "success"
        assert "bytes_written" in result["data"]
        assert result["data"]["path"] == "/path/to/output.txt"
        assert result["data"]["bytes_written"] == 12  # Length of "Test content"
        
        # Verify TEPS was called with the correct request
        self.teps_manager.execute_tool.assert_called_once_with(self.write_file_request)
    
    def test_process_bash_command_request(self):
        """Test processing an executeBashCommand tool request."""
        # Process the request
        result = self.tool_request_handler.process_tool_request(self.bash_command_request)
        
        # Verify the result
        assert isinstance(result, dict)
        assert result["request_id"] == "bash-789"
        assert result["tool_name"] == "executeBashCommand"
        assert result["status"] == "success"
        assert "Output of command: ls -la" in result["data"]
        
        # Verify TEPS was called with the correct request
        self.teps_manager.execute_tool.assert_called_once_with(self.bash_command_request)
    
    def test_error_handling(self):
        """Test handling of tool execution errors."""
        # Process the error-causing request
        with pytest.raises(ToolExecutionError) as exc_info:
            self.tool_request_handler.process_tool_request(self.error_tool_request)
        
        # Verify the exception
        assert "Simulated tool error" in str(exc_info.value)
        
        # Verify the error result is attached to the exception
        assert hasattr(exc_info.value, 'error_result')
        error_result = exc_info.value.error_result
        
        # Verify error result
        assert error_result["request_id"] == "error-999"
        assert error_result["tool_name"] == "errorTool"
        assert error_result["status"] == "error"
        assert "error_message" in error_result["data"]
        assert "Simulated tool error" in error_result["data"]["error_message"]
    
    def test_validation_error(self):
        """Test validation of tool requests."""
        # Process an invalid request
        with pytest.raises(ValueError) as exc_info:
            self.tool_request_handler.process_tool_request(self.invalid_request)
        
        # Verify the validation error
        assert "missing required field" in str(exc_info.value)
    
    def test_batch_processing(self):
        """Test batch processing of multiple tool requests."""
        # Create a batch of requests
        batch_requests = [
            self.read_file_request,
            self.write_file_request,
            self.bash_command_request,
            self.error_tool_request  # This will cause an error
        ]
        
        # Process the batch
        batch_results = self.tool_request_handler.process_batch_tool_requests(batch_requests)
        
        # Verify we have a result for each request
        assert len(batch_results) == 4
        
        # Verify the successful results
        assert batch_results[0]["tool_name"] == "readFile"
        assert batch_results[0]["status"] == "success"
        
        assert batch_results[1]["tool_name"] == "writeFile"
        assert batch_results[1]["status"] == "success"
        
        assert batch_results[2]["tool_name"] == "executeBashCommand"
        assert batch_results[2]["status"] == "success"
        
        # Verify the error result
        assert batch_results[3]["tool_name"] == "errorTool"
        assert batch_results[3]["status"] == "error"
        assert "error_message" in batch_results[3]["data"]
    
    def test_format_tool_result_as_message(self):
        """Test formatting of tool results as messages for conversation history."""
        # Process a tool request to get a result
        result = self.tool_request_handler.process_tool_request(self.read_file_request)
        
        # Format the result as a message
        message = self.tool_request_handler.format_tool_result_as_message(result)
        
        # Verify message format
        assert message["role"] == "tool_result"
        assert message["tool_name"] == "readFile"
        assert message["tool_call_id"] == "read-123"
        assert isinstance(message["content"], str)
        assert "Content of file" in message["content"]
        
        # Test with a structured data result
        write_result = self.tool_request_handler.process_tool_request(self.write_file_request)
        write_message = self.tool_request_handler.format_tool_result_as_message(write_result)
        
        # Verify that structured data is properly serialized
        assert write_message["role"] == "tool_result"
        assert write_message["tool_name"] == "writeFile"
        assert write_message["tool_call_id"] == "write-456"
        assert isinstance(write_message["content"], str)
        
        # Should be JSON-serialized object
        content_data = json.loads(write_message["content"])
        assert "bytes_written" in content_data
        assert "path" in content_data
    
    def test_serialization_failure_handling(self):
        """Test handling of serialization failures when formatting tool results."""
        # Create a mock result with unserializable data
        class UnserializableObject:
            def __repr__(self):
                return "<Unserializable Object>"
        
        mock_result = {
            "request_id": "mock-result",
            "tool_name": "mockTool",
            "status": "success",
            "data": {
                "unserializable": UnserializableObject()
            }
        }
        
        # Format the result - should use str() as fallback
        message = self.tool_request_handler.format_tool_result_as_message(mock_result)
        
        # Verify message
        assert message["role"] == "tool_result"
        assert message["tool_name"] == "mockTool"
        assert message["tool_call_id"] == "mock-result"
        assert isinstance(message["content"], str)
        assert "Unserializable" in message["content"]  # String representation should be used
    
    def test_tool_name_validation(self):
        """Test validation of tool_name field."""
        # Create a request with invalid tool_name (not a string)
        invalid_tool_name_request = {
            "request_id": "invalid-tool-name",
            "tool_name": 123,  # Not a string
            "parameters": {"param": "value"},
            "icerc_full_text": "Intent: Invalid\nCommand: None\nExpected: Error\nRisk: None\nConfirmation: [Y/N]"
        }
        
        # Process the request
        with pytest.raises(ValueError) as exc_info:
            self.tool_request_handler.process_tool_request(invalid_tool_name_request)
        
        # Verify error
        assert "tool_name must be a string" in str(exc_info.value)
    
    def test_parameters_validation(self):
        """Test validation of parameters field."""
        # Create a request with invalid parameters (not a dict)
        invalid_parameters_request = {
            "request_id": "invalid-parameters",
            "tool_name": "readFile",
            "parameters": "invalid-parameters",  # Not a dictionary
            "icerc_full_text": "Intent: Invalid\nCommand: None\nExpected: Error\nRisk: None\nConfirmation: [Y/N]"
        }
        
        # Process the request
        with pytest.raises(ValueError) as exc_info:
            self.tool_request_handler.process_tool_request(invalid_parameters_request)
        
        # Verify error
        assert "parameters must be a dictionary" in str(exc_info.value)
    
    def test_request_id_handling(self):
        """Test handling of requests with and without request_id."""
        # Create a request without a request_id
        no_request_id = {
            "tool_name": "readFile",
            "parameters": {"file_path": "/path/to/file.txt"},
            "icerc_full_text": "Intent: Read file\nCommand: Read file\nExpected: Content\nRisk: Low\nConfirmation: [Y/N]"
        }
        
        # Process the request
        result = self.tool_request_handler.process_tool_request(no_request_id)
        
        # Verify result has a default request_id
        assert "request_id" in result
        assert result["request_id"] == "req-123"  # Our mock's default
        
        # Format as message
        message = self.tool_request_handler.format_tool_result_as_message(result)
        
        # Verify message has the tool_call_id
        assert message["tool_call_id"] == "req-123"