#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for error handling across Framework Core Application components.

These tests verify that errors are properly handled, propagated, and recovered from
across component boundaries.

AI-GENERATED: [Forge] - Task:[RFI-COREAPP-INT-TEST-001]
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch, call
import json

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the google.generativeai module before importing components
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

from framework_core.message_manager import MessageManager
from framework_core.ui_manager import UserInterfaceManager
from framework_core.lial_core import LLMAdapterInterface
from framework_core.tool_request_handler import ToolRequestHandler
from framework_core.controller import FrameworkController
from framework_core.error_handler import ErrorHandler


class MockLLMAdapter(LLMAdapterInterface):
    """Mock LLM Adapter that can be configured to fail in different ways."""
    
    def __init__(self, config: dict, dcm_instance=None) -> None:
        """Initialize the mock adapter."""
        self.config = config
        self.dcm = dcm_instance
        self.message_sequence_history = []
        self.fail_on_nth_call = None
        self.error_message = "Mock LLM failure"
        self.call_count = 0
    
    def send_message_sequence(self, messages: list, active_persona_id: str = None) -> dict:
        """Mock sending a message sequence to the LLM with configurable failure."""
        self.message_sequence_history.append({
            'messages': messages.copy(),
            'persona_id': active_persona_id
        })
        
        self.call_count += 1
        
        # Check if we should fail this call
        if self.fail_on_nth_call and self.call_count == self.fail_on_nth_call:
            raise Exception(self.error_message)
        
        # Otherwise return a normal response
        return {
            "conversation": "This is a mock LLM response (call #" + str(self.call_count) + ")",
            "tool_request": None
        }
    
    def configure_failure(self, on_nth_call: int, error_message: str = None) -> None:
        """Configure the adapter to fail on a specific call."""
        self.fail_on_nth_call = on_nth_call
        if error_message:
            self.error_message = error_message


class MockTEPS:
    """Mock TEPS that can be configured to fail in different ways."""
    
    def __init__(self):
        """Initialize the mock TEPS."""
        self.call_count = 0
        self.fail_on_nth_call = None
        self.error_message = "Mock TEPS failure"
        self.fail_on_tool = None
    
    def execute_tool(self, tool_request: dict) -> dict:
        """Mock tool execution with configurable failure."""
        self.call_count += 1
        
        # Check if we should fail this call
        if self.fail_on_nth_call and self.call_count == self.fail_on_nth_call:
            raise Exception(self.error_message)
            
        # Check if we should fail for a specific tool
        if self.fail_on_tool and tool_request["tool_name"] == self.fail_on_tool:
            return {
                "request_id": tool_request["request_id"],
                "tool_name": tool_request["tool_name"],
                "status": "error",
                "error": {
                    "code": "TOOL_EXECUTION_FAILED",
                    "message": self.error_message
                }
            }
            
        # Otherwise return a success response
        return {
            "request_id": tool_request["request_id"],
            "tool_name": tool_request["tool_name"],
            "status": "success",
            "data": {
                "result": "Mock tool execution successful"
            }
        }
    
    def configure_failure(self, on_nth_call: int = None, on_tool: str = None, error_message: str = None) -> None:
        """Configure TEPS to fail in a specific way."""
        self.fail_on_nth_call = on_nth_call
        self.fail_on_tool = on_tool
        if error_message:
            self.error_message = error_message


class TestErrorHandlingIntegration(unittest.TestCase):
    """Integration tests for error handling across components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock output handler
        self.output_mock = MagicMock()
        
        # Create UI Manager with mock output
        self.ui_manager = UserInterfaceManager(
            config={"use_color": False},
            output_handler=self.output_mock
        )
        
        # Create Message Manager
        self.message_manager = MessageManager()
        
        # Create mock LIAL adapter
        self.mock_lial_adapter = MockLLMAdapter({})
        
        # Create mock TEPS
        self.mock_teps = MockTEPS()
        
        # Create tool request handler with mock TEPS
        self.tool_request_handler = ToolRequestHandler(self.mock_teps)
        
        # Create mock DCM Manager
        self.mock_dcm_manager = MagicMock()
        self.mock_dcm_manager.get_initial_prompt.return_value = "You are an AI assistant."
        
        # Create Error Handler
        self.error_handler = ErrorHandler()
        
        # Create Controller with mocked components
        self.controller = FrameworkController(MagicMock())
        self.controller.ui_manager = self.ui_manager
        self.controller.message_manager = self.message_manager
        self.controller.lial_manager = MagicMock()
        self.controller.lial_manager.send_messages.side_effect = self.mock_lial_adapter.send_message_sequence
        self.controller.dcm_manager = self.mock_dcm_manager
        self.controller.teps_manager = MagicMock()
        self.controller.teps_manager.execute_tool.side_effect = self.mock_teps.execute_tool
        self.controller.tool_request_handler = self.tool_request_handler
        self.controller.error_handler = self.error_handler
    
    def test_lial_communication_failure_recovery(self):
        """Test recovery from LLM API failures."""
        # Configure LIAL to fail on second call
        self.mock_lial_adapter.configure_failure(
            on_nth_call=2,
            error_message="LLM API connection error"
        )
        
        # Setup input to trigger multiple LLM calls
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["First message", "Second message (will fail)", "Third message (should recover)", "/quit"]
            
            # Run the controller
            self.controller.run()
        
        # Verify error was displayed
        error_calls = [call for call in self.output_mock.call_args_list 
                       if "[Error]:" in str(call) and "LLM API connection error" in str(call)]
        self.assertTrue(len(error_calls) > 0)
        
        # Verify controller recovered and processed the third message
        third_response_calls = [call for call in self.output_mock.call_args_list 
                                if "mock LLM response (call #3)" in str(call)]
        self.assertTrue(len(third_response_calls) > 0)
        
        # Verify message history was maintained through the error
        self.assertGreaterEqual(len(self.message_manager.messages), 5)  # At least 5 messages (system + 2 pairs)
    
    def test_tool_execution_exception_handling(self):
        """Test handling of exceptions during tool execution."""
        # Configure TEPS to throw an exception
        self.mock_teps.configure_failure(
            on_nth_call=1,
            error_message="Unhandled tool execution error"
        )
        
        # Configure LLM to request a tool
        tool_request = {
            "request_id": "test123",
            "tool_name": "testTool",
            "parameters": {"param": "value"}
        }
        
        self.mock_lial_adapter.send_message_sequence = MagicMock(return_value={
            "conversation": "I'll use a tool.",
            "tool_request": tool_request
        })
        
        # Setup input
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["Use a tool", "/quit"]
            
            # Run the controller
            self.controller.run()
        
        # Verify error was displayed
        error_calls = [call for call in self.output_mock.call_args_list 
                       if "[Error]:" in str(call) and "tool execution" in str(call).lower()]
        self.assertTrue(len(error_calls) > 0)
        
        # Verify error was added to message history as a tool result with error status
        tool_messages = [m for m in self.message_manager.messages if m.get("role") == "tool_result"]
        self.assertEqual(len(tool_messages), 1)
        self.assertIn("error", tool_messages[0])
    
    def test_tool_error_result_propagation(self):
        """Test that tool error results are correctly propagated to LLM."""
        # Configure TEPS to return an error result for a specific tool
        self.mock_teps.configure_failure(
            on_tool="readFile",
            error_message="File not found"
        )
        
        # Configure initial LLM response with tool request
        self.mock_lial_adapter.send_message_sequence = MagicMock(side_effect=[
            {
                "conversation": "I'll read that file for you.",
                "tool_request": {
                    "request_id": "read123",
                    "tool_name": "readFile",
                    "parameters": {"path": "/nonexistent/file.txt"}
                }
            },
            {
                "conversation": "I couldn't read the file because: File not found",
                "tool_request": None
            }
        ])
        
        # Setup input
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["Read a file", "/quit"]
            
            # Run the controller
            self.controller.run()
        
        # Verify error tool result was added to message history
        tool_messages = [m for m in self.message_manager.messages if m.get("role") == "tool_result"]
        self.assertEqual(len(tool_messages), 1)
        self.assertEqual(tool_messages[0]["status"], "error")
        
        # Verify LLM received the error result
        args, _ = self.mock_lial_adapter.send_message_sequence.call_args_list[1]
        messages = args[0]
        
        # Find the tool result message in the sent messages
        tool_result_message = next((m for m in messages if m.get("role") == "tool"), None)
        self.assertIsNotNone(tool_result_message)
        
        # Verify error acknowledgment was displayed
        error_ack_calls = [call for call in self.output_mock.call_args_list 
                           if "couldn't read the file" in str(call)]
        self.assertTrue(len(error_ack_calls) > 0)
    
    def test_component_initialization_failure(self):
        """Test recovery from component initialization failures."""
        # Create a function that will raise an exception when initializing a component
        def mock_init_component(component_name):
            if component_name == "message_manager":
                return MessageManager()
            elif component_name == "ui_manager":
                return UserInterfaceManager(output_handler=self.output_mock)
            elif component_name == "lial_manager":
                raise Exception("Failed to initialize LIAL Manager: API key missing")
            else:
                # Mock all other components
                return MagicMock()
        
        # Patch the controller's initialize_component method
        with patch.object(FrameworkController, '_initialize_component', side_effect=mock_init_component):
            # Create a fresh controller to test initialization
            test_controller = FrameworkController(MagicMock())
            
            # Initialize with expected failure
            with self.assertRaises(Exception) as context:
                test_controller.initialize_components()
                
            # Verify error message
            self.assertIn("Failed to initialize LIAL Manager", str(context.exception))
    
    def test_multiple_tool_requests_with_error_recovery(self):
        """Test a sequence of tool requests with one failing."""
        # Configure TEPS to fail only for a specific tool
        self.mock_teps.configure_failure(
            on_tool="failingTool",
            error_message="This tool is designed to fail"
        )
        
        # Configure LLM responses for a sequence of interactions
        self.mock_lial_adapter.send_message_sequence = MagicMock(side_effect=[
            # First response with successful tool request
            {
                "conversation": "I'll use the first tool.",
                "tool_request": {
                    "request_id": "tool1",
                    "tool_name": "successfulTool",
                    "parameters": {"param": "value1"}
                }
            },
            # Follow-up with failing tool request
            {
                "conversation": "Now I'll use another tool.",
                "tool_request": {
                    "request_id": "tool2",
                    "tool_name": "failingTool",
                    "parameters": {"param": "value2"}
                }
            },
            # Final response after tool failure
            {
                "conversation": "I encountered an error with the second tool. Let me try a third tool.",
                "tool_request": {
                    "request_id": "tool3",
                    "tool_name": "successfulTool2",
                    "parameters": {"param": "value3"}
                }
            },
            # Response after final tool success
            {
                "conversation": "All done with the tools.",
                "tool_request": None
            }
        ])
        
        # Setup input
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["Use multiple tools", "/quit"]
            
            # Run the controller
            self.controller.run()
        
        # Verify we have the expected sequence of messages in history
        assistant_messages = [m for m in self.message_manager.messages if m.get("role") == "assistant"]
        self.assertEqual(len(assistant_messages), 4)
        
        tool_messages = [m for m in self.message_manager.messages if m.get("role") == "tool_result"]
        self.assertEqual(len(tool_messages), 3)
        
        # Verify the second tool result has error status
        self.assertEqual(tool_messages[0]["status"], "success")
        self.assertEqual(tool_messages[1]["status"], "error")
        self.assertEqual(tool_messages[2]["status"], "success")
        
        # Verify all expected responses were displayed
        final_response_calls = [call for call in self.output_mock.call_args_list 
                                if "All done with the tools" in str(call)]
        self.assertTrue(len(final_response_calls) > 0)
    
    def test_user_interruption_recovery(self):
        """Test recovery from user interruptions."""
        # Setup input to simulate a user interruption (KeyboardInterrupt)
        with patch('builtins.input') as mock_input:
            # First input triggers normal flow, second raises KeyboardInterrupt, third continues normally
            def input_side_effect(prompt):
                if mock_input.call_count == 1:
                    return "First message"
                elif mock_input.call_count == 2:
                    raise KeyboardInterrupt()
                else:
                    return "/quit"
            
            mock_input.side_effect = input_side_effect
            
            # Run the controller
            self.controller.run()
        
        # Verify controller recovered from the interruption
        self.assertTrue(self.output_mock.call_count > 0)
        
        # Verify first message was processed
        first_response_calls = [call for call in self.output_mock.call_args_list 
                                if "mock LLM response" in str(call)]
        self.assertTrue(len(first_response_calls) > 0)
    
    def test_invalid_tool_request_handling(self):
        """Test handling of invalid tool requests from LLM."""
        # Configure LLM to return an invalid tool request (missing required fields)
        self.mock_lial_adapter.send_message_sequence = MagicMock(return_value={
            "conversation": "I'll use a tool.",
            "tool_request": {
                # Missing request_id
                "tool_name": "testTool",
                "parameters": {"param": "value"}
            }
        })
        
        # Setup input
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["Use a tool with invalid request", "/quit"]
            
            # Run the controller
            self.controller.run()
        
        # Verify error was displayed
        error_calls = [call for call in self.output_mock.call_args_list 
                       if "[Error]:" in str(call) and "invalid tool request" in str(call).lower()]
        self.assertTrue(len(error_calls) > 0)
        
        # Verify controller didn't crash
        quit_calls = [call for call in self.output_mock.call_args_list 
                      if "Goodbye" in str(call)]
        self.assertTrue(len(quit_calls) > 0)


if __name__ == "__main__":
    unittest.main()