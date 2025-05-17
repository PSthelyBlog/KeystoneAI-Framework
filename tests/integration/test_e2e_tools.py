"""
End-to-end tests for tool execution scenarios.

These tests verify that the framework correctly:
1. Handles tool requests and executions
2. Processes tool results and incorporates them into the conversation
3. Manages multiple sequential tool usages
4. Handles tool execution errors appropriately
"""

import pytest
import os
import sys
import uuid
from unittest.mock import MagicMock, patch, call

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.integration.utils import IntegrationTestCase
from tests.integration.e2e_fixtures import (
    ConversationScenario, 
    MockScenarioBuilder,
    assert_tool_was_executed, 
    assert_error_handled
)


class TestE2EToolExecution(IntegrationTestCase):
    """
    End-to-end tests for tool execution scenarios.
    
    These tests verify the framework's ability to handle tool requests,
    executions, and results in realistic conversation flows.
    """
    
    def test_basic_file_reading(self, e2e_controller, mock_conversation, scenario_builder, e2e_test_data):
        """Test a basic file reading scenario."""
        # Create a file reading scenario with a specific file path
        file_path = e2e_test_data["paths"]["text_file"]
        file_content = e2e_test_data["contents"][file_path]
        
        read_file_request_id = f"read-{str(uuid.uuid4())[:8]}"
        scenario = ConversationScenario(
            name="file_reading",
            description="Basic file reading scenario"
        ).add_user_input(
            f"Read the file at {file_path}"
        ).add_expected_llm_response(
            f"I'll read the file at {file_path} for you.",
            tool_request={
                "request_id": read_file_request_id,
                "tool_name": "readFile",
                "parameters": {"file_path": file_path}
            }
        ).add_tool_result(
            read_file_request_id,
            "readFile",
            file_content
        ).add_expected_llm_response(
            f"I've read the file. Here's what it contains:\n\n```\n{file_content}\n```"
        ).add_verification_step(
            lambda controller: assert_tool_was_executed(controller, "readFile"),
            "Verify readFile tool was executed"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify tool request flow
        assert controller.tool_request_handler.process_tool_request.call_count == 1
        assert controller.message_manager.add_tool_result_message.call_count == 1
        
        # Verify the second LLM call was made with the tool result
        assert controller.lial_manager.send_messages.call_count == 2
    
    def test_multiple_sequential_tools(self, e2e_controller, mock_conversation, e2e_test_data):
        """Test multiple sequential tool executions without user intervention."""
        # Create file paths and request IDs
        file_path1 = e2e_test_data["paths"]["text_file"]
        file_path2 = e2e_test_data["paths"]["python_file"]
        file_content1 = e2e_test_data["contents"][file_path1]
        file_content2 = e2e_test_data["contents"][file_path2]
        
        read_request_id1 = f"read-{str(uuid.uuid4())[:8]}"
        read_request_id2 = f"read-{str(uuid.uuid4())[:8]}"
        
        # Create a scenario with sequential tool requests
        scenario = ConversationScenario(
            name="sequential_tools",
            description="Multiple sequential tool executions"
        ).add_user_input(
            "First read the text file and then the Python file"
        ).add_expected_llm_response(
            "I'll read both files for you. Let me start with the text file.",
            tool_request={
                "request_id": read_request_id1,
                "tool_name": "readFile",
                "parameters": {"file_path": file_path1}
            }
        ).add_tool_result(
            read_request_id1,
            "readFile",
            file_content1
        ).add_expected_llm_response(
            f"I've read the text file. Now I'll read the Python file.",
            tool_request={
                "request_id": read_request_id2,
                "tool_name": "readFile",
                "parameters": {"file_path": file_path2}
            }
        ).add_tool_result(
            read_request_id2,
            "readFile",
            file_content2
        ).add_expected_llm_response(
            "I've read both files. Here are their contents:\n\n"
            f"Text file ({file_path1}):\n```\n{file_content1}\n```\n\n"
            f"Python file ({file_path2}):\n```python\n{file_content2}\n```"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify sequential tool requests were processed
        assert controller.tool_request_handler.process_tool_request.call_count == 2
        assert controller.message_manager.add_tool_result_message.call_count == 2
        assert controller.lial_manager.send_messages.call_count == 3
    
    def test_file_writing(self, e2e_controller, mock_conversation, e2e_test_data):
        """Test file writing tool usage."""
        # Define file path and content
        file_path = "/path/to/new-file.txt"
        file_content = "This is new content to write to the file."
        write_request_id = f"write-{str(uuid.uuid4())[:8]}"
        
        # Create a scenario for file writing
        scenario = ConversationScenario(
            name="file_writing",
            description="File writing scenario"
        ).add_user_input(
            f"Write '{file_content}' to {file_path}"
        ).add_expected_llm_response(
            f"I'll write the content to {file_path} for you.",
            tool_request={
                "request_id": write_request_id,
                "tool_name": "writeFile",
                "parameters": {
                    "file_path": file_path,
                    "content": file_content
                }
            }
        ).add_tool_result(
            write_request_id,
            "writeFile",
            {"bytes_written": len(file_content), "path": file_path}
        ).add_expected_llm_response(
            f"I've successfully written the content to {file_path}."
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify file writing tool was used
        tool_calls = controller.tool_request_handler.process_tool_request.call_args_list
        assert len(tool_calls) == 1
        
        # Extract tool request details
        args, kwargs = tool_calls[0]
        tool_request = args[0]
        
        # Verify tool request parameters
        assert tool_request["tool_name"] == "writeFile"
        assert tool_request["parameters"]["file_path"] == file_path
        assert tool_request["parameters"]["content"] == file_content
    
    def test_command_execution(self, e2e_controller, mock_conversation):
        """Test command execution tool usage."""
        # Define command and output
        command = "ls -la"
        command_output = "total 20\ndrwxr-xr-x  5 user user 4096 May 17 12:00 .\ndrwxr-xr-x 10 user user 4096 May 17 11:55 .."
        bash_request_id = f"bash-{str(uuid.uuid4())[:8]}"
        
        # Create a scenario for command execution
        scenario = ConversationScenario(
            name="command_execution",
            description="Command execution scenario"
        ).add_user_input(
            f"Run the command: {command}"
        ).add_expected_llm_response(
            f"I'll run the command '{command}' for you.",
            tool_request={
                "request_id": bash_request_id,
                "tool_name": "executeBashCommand",
                "parameters": {"command": command}
            }
        ).add_tool_result(
            bash_request_id,
            "executeBashCommand",
            command_output
        ).add_expected_llm_response(
            f"I ran the command `{command}`. Here's the output:\n\n```\n{command_output}\n```"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify command execution tool was used
        tool_calls = controller.tool_request_handler.process_tool_request.call_args_list
        assert len(tool_calls) == 1
        
        # Extract tool request details
        args, kwargs = tool_calls[0]
        tool_request = args[0]
        
        # Verify tool request parameters
        assert tool_request["tool_name"] == "executeBashCommand"
        assert tool_request["parameters"]["command"] == command
    
    def test_tool_error_handling(self, e2e_controller, mock_conversation, scenario_builder):
        """Test handling of tool execution errors."""
        # Use the pre-built error scenario from our builder
        scenario = scenario_builder.create_error_scenario()
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Enable debug mode to test error display
        controller.debug_mode = True
        
        # Run the controller
        controller.run()
        
        # Verify error handling
        assert controller.error_handler.handle_error.call_count >= 1
        assert controller.ui_manager.display_error_message.call_count >= 1
        
        # Verify that after error, the conversation continued
        assert controller.lial_manager.send_messages.call_count == 2
        
        # Run verification steps
        for verification_func, description in scenario.verification_steps:
            verification_func(controller)
    
    def test_tool_handler_missing(self, e2e_controller, mock_conversation):
        """Test behavior when tool request handler is not initialized."""
        # Define tool request
        read_request_id = f"read-{str(uuid.uuid4())[:8]}"
        scenario = ConversationScenario(
            name="missing_handler",
            description="Tool handler missing scenario"
        ).add_user_input(
            "Read a file for me"
        ).add_expected_llm_response(
            "I'll read that file for you.",
            tool_request={
                "request_id": read_request_id,
                "tool_name": "readFile",
                "parameters": {"file_path": "/path/to/file.txt"}
            }
        ).add_expected_llm_response(
            "I'm sorry, but I'm currently unable to perform file operations. Is there something else I can help you with?"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Remove the tool request handler to simulate missing handler
        controller.tool_request_handler = None
        
        # Run the controller
        controller.run()
        
        # Verify the conversation continued despite missing handler
        assert controller.lial_manager.send_messages.call_count == 2
        assert controller.message_manager.add_assistant_message.call_count == 2
    
    def test_debug_mode_tool_display(self, e2e_controller, mock_conversation):
        """Test that tool results are displayed in debug mode."""
        # Define request and result
        read_request_id = f"read-{str(uuid.uuid4())[:8]}"
        file_content = "Debug mode test file content."
        
        # Create a scenario for testing debug display
        scenario = ConversationScenario(
            name="debug_mode",
            description="Debug mode tool display"
        ).add_user_input(
            "Read a file with debug mode on"
        ).add_expected_llm_response(
            "I'll read that file for you.",
            tool_request={
                "request_id": read_request_id,
                "tool_name": "readFile",
                "parameters": {"file_path": "/path/to/file.txt"}
            }
        ).add_tool_result(
            read_request_id,
            "readFile",
            file_content
        ).add_expected_llm_response(
            f"I've read the file. Here's what it contains:\n\n```\n{file_content}\n```"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Enable debug mode
        controller.debug_mode = True
        
        # Run the controller
        controller.run()
        
        # Verify debug info was displayed
        debug_displays = [
            call for call in controller.ui_manager.display_system_message.call_args_list
            if "Tool 'readFile' executed with result" in call[0][0]
        ]
        assert len(debug_displays) >= 1