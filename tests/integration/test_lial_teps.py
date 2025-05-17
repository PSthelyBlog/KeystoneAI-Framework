"""
Integration tests for LIAL-TEPS component chain.

These tests verify the integration between the LLM Interaction Abstraction Layer (LIAL)
and the Tool Execution & Permission Service (TEPS) components.
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.exceptions import LIALInitError, TEPSInitError, ToolExecutionError
from framework_core.component_managers.lial_manager import LIALManager
from framework_core.component_managers.teps_manager import TEPSManager
from framework_core.lial_core import Message, LLMResponse, ToolRequest, ToolResult
from framework_core.tool_request_handler import ToolRequestHandler
from tests.integration.utils import MockLLMAdapter, ResponseBuilder, IntegrationTestCase


class TestLIALTEPSIntegration(IntegrationTestCase):
    """
    Integration tests for the LIAL-TEPS chain.
    
    These tests validate that:
    1. LIAL properly generates tool requests that TEPS can understand
    2. TEPS correctly executes tool requests from LIAL
    3. Tool results are properly formatted for LLM follow-up
    4. Error conditions are handled appropriately
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        super().setup_method()
        
        # Create mock DCM instance for LLM adapter
        self.dcm_instance = MagicMock(name="DynamicContextManager")
        
        # Create mock LLM adapter
        self.llm_adapter = MockLLMAdapter(
            config={"model_name": "mock-model", "temperature": 0.7},
            dcm_instance=self.dcm_instance
        )
        
        # Configure standard responses
        self.llm_adapter.configure_response("default", {
            "conversation": "I am an AI assistant. How can I help you?",
            "tool_request": None
        })
        
        # Configure tool request responses
        self.llm_adapter.configure_response("read_file", ResponseBuilder.tool_request(
            tool_name="readFile",
            parameters={"file_path": "/path/to/file.txt"},
            conversation_text="I'll read that file for you.",
            request_id="read-123"
        ))
        
        self.llm_adapter.configure_response("write_file", ResponseBuilder.tool_request(
            tool_name="writeFile",
            parameters={"file_path": "/path/to/file.txt", "content": "New content"},
            conversation_text="I'll write to that file for you.",
            request_id="write-456"
        ))
        
        self.llm_adapter.configure_response("execute_command", ResponseBuilder.tool_request(
            tool_name="executeBashCommand",
            parameters={"command": "ls -la"},
            conversation_text="I'll run that command for you.",
            request_id="bash-789"
        ))
        
        # Add pattern matchers
        self.llm_adapter.configure_pattern("read file", "read_file")
        self.llm_adapter.configure_pattern("write file", "write_file")
        self.llm_adapter.configure_pattern("run command", "execute_command")
        
        # Create LIAL manager with our mock adapter
        self.lial_manager = MagicMock(name="LIALManager")
        self.lial_manager.send_messages.side_effect = self.llm_adapter.send_message_sequence
        
        # Create mock TEPS instance
        self.teps_instance = MagicMock(name="TEPSEngine")
        
        # Configure TEPS execute_tool with appropriate responses
        def mock_execute_tool(tool_request):
            tool_name = tool_request.get("tool_name", "unknown")
            request_id = tool_request.get("request_id", "unknown")
            
            if tool_name == "readFile":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": "Content of the requested file."
                }
            elif tool_name == "writeFile":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": {"bytes_written": 123, "path": tool_request.get("parameters", {}).get("file_path")}
                }
            elif tool_name == "executeBashCommand":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": "Command output here"
                }
            elif "error" in tool_name.lower():
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {"error_message": "Tool execution failed"}
                }
            else:
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": {"message": "Tool executed successfully"}
                }
        
        self.teps_instance.execute_tool.side_effect = mock_execute_tool
        
        # Create TEPS manager with our mock TEPS instance
        self.teps_manager = MagicMock(name="TEPSManager")
        self.teps_manager.teps_instance = self.teps_instance
        self.teps_manager.execute_tool.side_effect = self.teps_instance.execute_tool
        
        # Create ToolRequestHandler with our TEPS manager
        self.tool_request_handler = ToolRequestHandler(teps_manager=self.teps_manager)
        
        # Create test message sequences
        self.basic_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Hello, who are you?")
        ])
        
        self.read_file_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Can you read file /path/to/file.txt?")
        ])
        
        self.write_file_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Please write file /path/to/file.txt with content 'New content'")
        ])
        
        self.execute_command_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Run command 'ls -la'")
        ])
    
    def test_lial_tool_request_generation(self):
        """Test that LIAL properly generates tool requests."""
        # Send messages that should trigger tool requests
        read_file_response = self.lial_manager.send_messages(self.read_file_messages)
        write_file_response = self.lial_manager.send_messages(self.write_file_messages)
        execute_command_response = self.lial_manager.send_messages(self.execute_command_messages)
        
        # Verify read file response
        assert read_file_response["tool_request"] is not None
        assert read_file_response["tool_request"]["tool_name"] == "readFile"
        assert read_file_response["tool_request"]["parameters"]["file_path"] == "/path/to/file.txt"
        
        # Verify write file response
        assert write_file_response["tool_request"] is not None
        assert write_file_response["tool_request"]["tool_name"] == "writeFile"
        assert write_file_response["tool_request"]["parameters"]["file_path"] == "/path/to/file.txt"
        assert write_file_response["tool_request"]["parameters"]["content"] == "New content"
        
        # Verify execute command response
        assert execute_command_response["tool_request"] is not None
        assert execute_command_response["tool_request"]["tool_name"] == "executeBashCommand"
        assert execute_command_response["tool_request"]["parameters"]["command"] == "ls -la"
    
    def test_teps_tool_execution(self):
        """Test that TEPS correctly executes tool requests from LIAL."""
        # Get tool requests from LIAL
        read_file_response = self.lial_manager.send_messages(self.read_file_messages)
        write_file_response = self.lial_manager.send_messages(self.write_file_messages)
        execute_command_response = self.lial_manager.send_messages(self.execute_command_messages)
        
        # Execute tool requests through ToolRequestHandler
        read_file_result = self.tool_request_handler.process_tool_request(read_file_response["tool_request"])
        write_file_result = self.tool_request_handler.process_tool_request(write_file_response["tool_request"])
        execute_command_result = self.tool_request_handler.process_tool_request(execute_command_response["tool_request"])
        
        # Verify read file result
        assert read_file_result["status"] == "success"
        assert read_file_result["tool_name"] == "readFile"
        assert read_file_result["request_id"] == read_file_response["tool_request"]["request_id"]
        assert read_file_result["data"] == "Content of the requested file."
        
        # Verify write file result
        assert write_file_result["status"] == "success"
        assert write_file_result["tool_name"] == "writeFile"
        assert write_file_result["request_id"] == write_file_response["tool_request"]["request_id"]
        assert write_file_result["data"]["bytes_written"] == 123
        assert write_file_result["data"]["path"] == "/path/to/file.txt"
        
        # Verify execute command result
        assert execute_command_result["status"] == "success"
        assert execute_command_result["tool_name"] == "executeBashCommand"
        assert execute_command_result["request_id"] == execute_command_response["tool_request"]["request_id"]
        assert execute_command_result["data"] == "Command output here"
    
    def test_tool_result_formatting(self):
        """Test that tool results are properly formatted for LLM follow-up."""
        # Get a tool request from LIAL
        read_file_response = self.lial_manager.send_messages(self.read_file_messages)
        
        # Execute tool request through ToolRequestHandler
        read_file_result = self.tool_request_handler.process_tool_request(read_file_response["tool_request"])
        
        # Format result as a message
        formatted_result = self.tool_request_handler.format_tool_result_as_message(read_file_result)
        
        # Verify formatting
        assert formatted_result["role"] == "tool_result"
        assert formatted_result["content"] == "Content of the requested file."
        assert formatted_result["tool_name"] == "readFile"
        assert formatted_result["tool_call_id"] == read_file_response["tool_request"]["request_id"]
        
        # Try with a more complex result (write_file)
        write_file_response = self.lial_manager.send_messages(self.write_file_messages)
        write_file_result = self.tool_request_handler.process_tool_request(write_file_response["tool_request"])
        formatted_write_result = self.tool_request_handler.format_tool_result_as_message(write_file_result)
        
        # Verify JSON formatting of complex data
        assert formatted_write_result["role"] == "tool_result"
        assert "bytes_written" in formatted_write_result["content"]
        assert "path" in formatted_write_result["content"]
        assert formatted_write_result["tool_name"] == "writeFile"
    
    def test_lial_teps_error_handling(self):
        """Test error handling in the LIAL-TEPS chain."""
        # Configure LLM adapter for an error-causing tool
        self.llm_adapter.configure_response("error_tool", ResponseBuilder.tool_request(
            tool_name="errorTool",
            parameters={"param": "value"},
            conversation_text="I'll try this tool for you.",
            request_id="error-999"
        ))
        self.llm_adapter.configure_pattern("cause error", "error_tool")
        
        # Create a message that should trigger the error tool
        error_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Please cause error with a tool.")
        ])
        
        # Get the error tool request
        error_response = self.lial_manager.send_messages(error_messages)
        
        # Execute the error tool request
        error_result = self.tool_request_handler.process_tool_request(error_response["tool_request"])
        
        # Verify the error result
        assert error_result["status"] == "error"
        assert error_result["tool_name"] == "errorTool"
        assert error_result["request_id"] == error_response["tool_request"]["request_id"]
        assert "error_message" in error_result["data"]
        
        # Format error as a message
        formatted_error = self.tool_request_handler.format_tool_result_as_message(error_result)
        
        # Verify error formatting
        assert formatted_error["role"] == "tool_result"
        assert "error_message" in formatted_error["content"]
        assert formatted_error["tool_name"] == "errorTool"
    
    def test_teps_execution_exception(self):
        """Test handling of exceptions during TEPS execution."""
        # Modify the TEPS instance to raise an exception for a specific tool
        def mock_execute_with_exception(tool_request):
            if tool_request.get("tool_name") == "exceptionTool":
                raise ToolExecutionError("Simulated execution error")
            return self.teps_instance.execute_tool(tool_request)
        
        self.teps_manager.execute_tool.side_effect = mock_execute_with_exception
        
        # Configure LLM adapter for the exception tool
        self.llm_adapter.configure_response("exception_tool", ResponseBuilder.tool_request(
            tool_name="exceptionTool",
            parameters={"param": "value"},
            conversation_text="I'll try this exception-generating tool.",
            request_id="exception-888"
        ))
        self.llm_adapter.configure_pattern("throw exception", "exception_tool")
        
        # Create message that triggers the exception tool
        exception_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Please throw exception with a tool.")
        ])
        
        # Get the exception tool request
        exception_response = self.lial_manager.send_messages(exception_messages)
        
        # Execute the tool request - should raise an exception
        with pytest.raises(ToolExecutionError) as exc_info:
            self.tool_request_handler.process_tool_request(exception_response["tool_request"])
        
        assert "Simulated execution error" in str(exc_info.value)
    
    def test_full_conversation_with_tool_execution(self):
        """Test a full conversation flow including tool execution and result handling."""
        # Configure LLM adapter for multi-turn conversation with tool
        self.llm_adapter.configure_response("after_tool", {
            "conversation": "I've processed the file content: 'Content of the requested file.'",
            "tool_request": None
        })
        
        # First, get a tool request
        read_file_response = self.lial_manager.send_messages(self.read_file_messages)
        
        # Execute the tool
        read_file_result = self.tool_request_handler.process_tool_request(read_file_response["tool_request"])
        
        # Format the result
        formatted_result = self.tool_request_handler.format_tool_result_as_message(read_file_result)
        
        # Create follow-up message sequence including tool result
        follow_up_messages = self.read_file_messages + [
            {"role": "assistant", "content": read_file_response["conversation"]},
            {
                "role": "tool",  # Note: Converted from tool_result to tool for LLM
                "content": formatted_result["content"],
                "name": formatted_result["tool_name"],
                "tool_call_id": formatted_result["tool_call_id"]
            }
        ]
        
        # Configure a specific response for the follow-up
        self.llm_adapter.configure_response("with_tool_result", {
            "conversation": f"I've processed the file content: '{formatted_result['content']}'",
            "tool_request": None
        })
        
        # Save original behavior
        original_find_matching_response = self.llm_adapter._find_matching_response
        
        # Override the method to return our specific response
        def custom_matcher(messages, active_persona_id):
            # Check if this is our follow-up message with tool result
            for msg in messages:
                if msg.get("role") == "tool" and msg.get("name") == "readFile":
                    return self.llm_adapter.responses["with_tool_result"]
            return original_find_matching_response(messages, active_persona_id)
        
        self.llm_adapter._find_matching_response = custom_matcher
        
        # Send follow-up message sequence including tool result
        follow_up_response = self.lial_manager.send_messages(follow_up_messages)
        
        # Restore original method
        self.llm_adapter._find_matching_response = original_find_matching_response
        
        # Verify the follow-up response references the tool result
        assert "I've processed the file content" in follow_up_response["conversation"]
        assert "Content of the requested file" in follow_up_response["conversation"]
    
    def test_multiple_tool_requests_sequence(self):
        """Test handling a sequence of multiple tool requests."""
        # Configure LLM adapter for a sequence of tools
        self.llm_adapter.configure_response("sequence_step1", ResponseBuilder.tool_request(
            tool_name="readFile",
            parameters={"file_path": "/path/to/input.txt"},
            conversation_text="First, I'll read the input file.",
            request_id="seq-read-123"
        ))
        
        self.llm_adapter.configure_response("sequence_step2", ResponseBuilder.tool_request(
            tool_name="writeFile",
            parameters={"file_path": "/path/to/output.txt", "content": "Processed content"},
            conversation_text="Now I'll write the processed content to an output file.",
            request_id="seq-write-456"
        ))
        
        self.llm_adapter.configure_response("sequence_complete", {
            "conversation": "I've completed the sequence of operations.",
            "tool_request": None
        })
        
        # Start with a request to process a file
        sequence_start_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Read the file at /path/to/input.txt, process it, and write the result to /path/to/output.txt")
        ])
        
        # Create a direct response sequence for our test
        def get_sequence_response(step):
            responses = {
                0: self.llm_adapter.responses["sequence_step1"],
                1: self.llm_adapter.responses["sequence_step2"],
                2: self.llm_adapter.responses["sequence_complete"]
            }
            return responses.get(step, responses[0])
        
        # Create a counter to track which step we're on
        sequence_step_counter = [0]  # Using a list for mutable state
        
        # Define a mock send_messages that returns our predefined sequence
        def sequence_handler(messages, active_persona_id=None):
            # Get current step response
            response = get_sequence_response(sequence_step_counter[0])
            # Increment for next call
            sequence_step_counter[0] += 1
            return response
        
        # Save original and replace temporarily
        original_send = self.lial_manager.send_messages
        self.lial_manager.send_messages = sequence_handler
        
        # Step 1: Get first tool request
        step1_response = self.lial_manager.send_messages(sequence_start_messages)
        assert step1_response["tool_request"]["tool_name"] == "readFile"
        
        # Execute first tool
        step1_result = self.tool_request_handler.process_tool_request(step1_response["tool_request"])
        step1_formatted = self.tool_request_handler.format_tool_result_as_message(step1_result)
        
        # Add first result to conversation
        sequence_step2_messages = sequence_start_messages + [
            {"role": "assistant", "content": step1_response["conversation"]},
            {
                "role": "tool",
                "content": step1_formatted["content"],
                "name": step1_formatted["tool_name"],
                "tool_call_id": step1_formatted["tool_call_id"]
            }
        ]
        
        # Step 2: Get second tool request
        step2_response = self.lial_manager.send_messages(sequence_step2_messages)
        assert step2_response["tool_request"]["tool_name"] == "writeFile"
        
        # Execute second tool
        step2_result = self.tool_request_handler.process_tool_request(step2_response["tool_request"])
        step2_formatted = self.tool_request_handler.format_tool_result_as_message(step2_result)
        
        # Add second result to conversation
        sequence_complete_messages = sequence_step2_messages + [
            {"role": "assistant", "content": step2_response["conversation"]},
            {
                "role": "tool",
                "content": step2_formatted["content"],
                "name": step2_formatted["tool_name"],
                "tool_call_id": step2_formatted["tool_call_id"]
            }
        ]
        
        # Step 3: Get completion message
        final_response = self.lial_manager.send_messages(sequence_complete_messages)
        
        # Restore original method
        self.lial_manager.send_messages = original_send
        
        # Verify final response has no tool request and includes completion message
        assert final_response["tool_request"] is None
        assert "completed the sequence" in final_response["conversation"]