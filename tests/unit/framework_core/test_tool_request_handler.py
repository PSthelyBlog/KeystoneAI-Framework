"""
Unit tests for the Tool Request Handler.
"""

import unittest
from unittest.mock import patch, MagicMock

from framework_core.tool_request_handler import ToolRequestHandler
from framework_core.exceptions import ToolExecutionError

class TestToolRequestHandler(unittest.TestCase):
    """Test cases for ToolRequestHandler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_teps_manager = MagicMock()
        self.handler = ToolRequestHandler(self.mock_teps_manager)
        
        # Sample tool request
        self.sample_request = {
            "request_id": "req123",
            "tool_name": "test_tool",
            "parameters": {
                "param1": "value1",
                "param2": "value2"
            }
        }
        
        # Sample tool result
        self.sample_result = {
            "request_id": "req123",
            "tool_name": "test_tool",
            "status": "success",
            "data": {
                "result": "Tool execution successful"
            }
        }
        
        # Configure mock to return the sample result
        self.mock_teps_manager.execute_tool.return_value = self.sample_result
        
    def test_process_tool_request_success(self):
        """Test processing a tool request successfully."""
        result = self.handler.process_tool_request(self.sample_request)
        
        # Verify TEPS manager was called with correct request
        self.mock_teps_manager.execute_tool.assert_called_once_with(self.sample_request)
        
        # Verify result is passed through
        self.assertEqual(result, self.sample_result)
        
    def test_process_tool_request_validation_error(self):
        """Test validation error for invalid tool request."""
        # Missing required field
        invalid_request = {
            "request_id": "req123",
            "tool_name": "test_tool"
            # Missing 'parameters'
        }
        
        with self.assertRaises(ValueError):
            self.handler.process_tool_request(invalid_request)
            
        # Invalid type for tool_name
        invalid_request = {
            "request_id": "req123",
            "tool_name": 123,  # Should be string
            "parameters": {}
        }
        
        with self.assertRaises(ValueError):
            self.handler.process_tool_request(invalid_request)
            
    def test_process_tool_request_execution_error(self):
        """Test handling of tool execution errors."""
        # Configure mock to raise an exception
        self.mock_teps_manager.execute_tool.side_effect = Exception("Tool execution failed")
        
        with self.assertRaises(ToolExecutionError):
            self.handler.process_tool_request(self.sample_request)
            
    def test_process_batch_tool_requests(self):
        """Test processing multiple tool requests in batch."""
        # Create a second request
        second_request = {
            "request_id": "req456",
            "tool_name": "other_tool",
            "parameters": {
                "param1": "valueA"
            }
        }
        
        # Configure mock to return different results for each call
        second_result = {
            "request_id": "req456",
            "tool_name": "other_tool",
            "status": "success",
            "data": {
                "result": "Second tool execution successful"
            }
        }
        
        self.mock_teps_manager.execute_tool.side_effect = [
            self.sample_result,
            second_result
        ]
        
        # Process batch
        results = self.handler.process_batch_tool_requests([self.sample_request, second_request])
        
        # Verify both requests were processed
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["request_id"], "req123")
        self.assertEqual(results[1]["request_id"], "req456")
        
    def test_batch_continues_after_error(self):
        """Test that batch processing continues after an error."""
        # Configure mock to raise an exception on first call but succeed on second
        second_result = {
            "request_id": "req456",
            "tool_name": "other_tool",
            "status": "success",
            "data": {
                "result": "Second tool execution successful"
            }
        }
        
        self.mock_teps_manager.execute_tool.side_effect = [
            Exception("First tool failed"),
            second_result
        ]
        
        # Create a second request
        second_request = {
            "request_id": "req456",
            "tool_name": "other_tool",
            "parameters": {
                "param1": "valueA"
            }
        }
        
        # Process batch
        results = self.handler.process_batch_tool_requests([self.sample_request, second_request])
        
        # Verify both requests were processed
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "error")  # First request failed
        self.assertEqual(results[1]["status"], "success")  # Second request succeeded
        
    def test_format_tool_result_as_message(self):
        """Test formatting a tool result as a message."""
        message = self.handler.format_tool_result_as_message(self.sample_result)
        
        # Verify message format
        self.assertEqual(message["role"], "tool_result")
        self.assertEqual(message["tool_name"], "test_tool")
        self.assertEqual(message["tool_call_id"], "req123")
        
        # Content should be serialized
        self.assertIsInstance(message["content"], str)

if __name__ == "__main__":
    unittest.main()