"""
Fixtures and utilities for end-to-end integration testing.

This module provides pytest fixtures and utility functions specifically designed
for end-to-end testing of the KeystoneAI-Framework, including:
- Enhanced mock components
- Scenario-based LLM response configuration
- Conversation simulation utilities
- Test data management
"""

import os
import sys
import pytest
import json
import uuid
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from unittest.mock import MagicMock, patch

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.exceptions import (
    ConfigError, 
    DCMInitError, 
    LIALInitError, 
    TEPSInitError,
    ComponentInitError,
    ToolExecutionError
)
from framework_core.lial_core import Message, LLMResponse, ToolRequest, ToolResult

from tests.integration.utils import MockLLMAdapter, ResponseBuilder, MockIOCapture, IntegrationTestCase
from tests.integration.conftest import (
    mock_minimal_config,
    mock_complete_config,
    mock_io_capture,
    mock_dcm_instance,
    mock_dcm_manager,
    mock_llm_adapter,
    mock_lial_manager,
    mock_teps_instance,
    mock_teps_manager,
    mock_message_manager,
    mock_ui_manager,
    mock_tool_request_handler,
    mock_error_handler,
    framework_controller_factory
)


class ConversationScenario:
    """
    Utility class for defining and executing conversation scenarios.
    
    This class helps structure end-to-end tests by providing a way to define
    a sequence of user inputs, expected LLM responses, and verification steps.
    """
    
    def __init__(self, 
                 name: str,
                 description: str = ""):
        """
        Initialize a conversation scenario.
        
        Args:
            name: Name of the scenario
            description: Description of what the scenario tests
        """
        self.name = name
        self.description = description
        self.user_inputs = []
        self.expected_llm_responses = []
        self.tool_results = {}
        self.verification_steps = []
    
    def add_user_input(self, user_input: str) -> 'ConversationScenario':
        """
        Add a user input to the scenario.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Self for chaining
        """
        self.user_inputs.append(user_input)
        return self
    
    def add_expected_llm_response(self, 
                                 conversation_text: str,
                                 tool_request: Optional[Dict[str, Any]] = None) -> 'ConversationScenario':
        """
        Add an expected LLM response to the scenario.
        
        Args:
            conversation_text: Expected conversation text from LLM
            tool_request: Optional tool request from LLM
            
        Returns:
            Self for chaining
        """
        response = {
            "conversation": conversation_text,
            "tool_request": tool_request
        }
        self.expected_llm_responses.append(response)
        return self
    
    def add_tool_result(self, 
                       request_id: str,
                       tool_name: str,
                       content: Union[str, Dict[str, Any]],
                       status: str = "success") -> 'ConversationScenario':
        """
        Add an expected tool result to the scenario.
        
        Args:
            request_id: ID of the tool request
            tool_name: Name of the tool
            content: Content of the tool result
            status: Status of the tool execution
            
        Returns:
            Self for chaining
        """
        self.tool_results[request_id] = {
            "request_id": request_id,
            "tool_name": tool_name,
            "status": status,
            "data": content
        }
        return self
    
    def add_verification_step(self, 
                             verification_func: Callable[[Any], None],
                             step_description: str = "") -> 'ConversationScenario':
        """
        Add a verification step to the scenario.
        
        Args:
            verification_func: Function that performs verification
            step_description: Description of what is being verified
            
        Returns:
            Self for chaining
        """
        self.verification_steps.append((verification_func, step_description))
        return self
    
    def configure_mock_llm(self, mock_llm: MockLLMAdapter) -> None:
        """
        Configure the mock LLM with expected responses for this scenario.
        
        Args:
            mock_llm: The mock LLM adapter to configure
        """
        # Clear any previous configuration
        mock_llm.clear_configurations()
        
        # Configure responses for each step
        for i, response in enumerate(self.expected_llm_responses):
            response_key = f"{self.name}_step_{i}"
            mock_llm.configure_response(response_key, response)
            
            # If this is a user input triggered response, add pattern
            if i < len(self.user_inputs):
                user_input = self.user_inputs[i]
                mock_llm.configure_pattern(user_input[:20], response_key)
    
    def configure_mock_teps(self, mock_teps: MagicMock) -> None:
        """
        Configure the mock TEPS with expected tool results for this scenario.
        
        Args:
            mock_teps: The mock TEPS instance to configure
        """
        # Create a side effect function for execute_tool
        def execute_tool_side_effect(tool_request):
            request_id = tool_request.get("request_id", "unknown")
            if request_id in self.tool_results:
                return self.tool_results[request_id]
            else:
                # Default fallback response
                tool_name = tool_request.get("tool_name", "unknown")
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": f"Default response for {tool_name}"
                }
        
        # Set the side effect
        mock_teps.execute_tool.side_effect = execute_tool_side_effect


class MockScenarioBuilder:
    """
    Utility for building mock scenarios for end-to-end testing.
    
    This class provides methods for creating realistic mock data
    and predefined scenarios for common testing patterns.
    """
    
    @staticmethod
    def create_basic_conversation() -> ConversationScenario:
        """
        Create a basic conversation scenario without tool usage.
        
        Returns:
            ConversationScenario configured for basic conversation
        """
        return ConversationScenario(
            name="basic_conversation",
            description="Basic conversation without tool usage"
        ).add_user_input(
            "Hello, how are you today?"
        ).add_expected_llm_response(
            "I'm doing well, thank you for asking! I'm the KeystoneAI-Framework assistant. How can I help you today?"
        ).add_user_input(
            "What capabilities do you have?"
        ).add_expected_llm_response(
            "As the KeystoneAI-Framework assistant, I can help with a variety of tasks. "
            "I can answer questions, assist with code, read and write files, and execute commands. "
            "I can also help explain the framework architecture and components."
        ).add_verification_step(
            lambda controller: assert_message_count(controller, 4),
            "Verify message count is correct"
        )
    
    @staticmethod
    def create_tool_usage_scenario() -> ConversationScenario:
        """
        Create a scenario involving tool usage.
        
        Returns:
            ConversationScenario configured for tool usage
        """
        read_file_request_id = f"read-{str(uuid.uuid4())[:8]}"
        return ConversationScenario(
            name="tool_usage",
            description="Conversation with tool usage"
        ).add_user_input(
            "Can you read the file at /path/to/example.txt?"
        ).add_expected_llm_response(
            "I'll read that file for you.",
            tool_request={
                "request_id": read_file_request_id,
                "tool_name": "readFile",
                "parameters": {"file_path": "/path/to/example.txt"}
            }
        ).add_tool_result(
            read_file_request_id,
            "readFile",
            "This is the content of the example file."
        ).add_expected_llm_response(
            "I've read the file. Here's what it contains:\n\n```\nThis is the content of the example file.\n```"
        ).add_verification_step(
            lambda controller: assert_tool_was_executed(controller, "readFile"),
            "Verify readFile tool was executed"
        )
    
    @staticmethod
    def create_command_scenario() -> ConversationScenario:
        """
        Create a scenario involving special command usage.
        
        Returns:
            ConversationScenario configured for special command usage
        """
        return ConversationScenario(
            name="special_commands",
            description="Usage of special commands"
        ).add_user_input(
            "/help"
        ).add_user_input(
            "/system You are a helpful assistant that specializes in Python programming."
        ).add_user_input(
            "What's your specialty?"
        ).add_expected_llm_response(
            "My specialty is Python programming. I can help you with Python code, libraries, best practices, and debugging."
        ).add_verification_step(
            lambda controller: assert_system_message_added(controller, "You are a helpful assistant that specializes in Python programming."),
            "Verify system message was added"
        )
    
    @staticmethod
    def create_error_scenario() -> ConversationScenario:
        """
        Create a scenario involving error handling.
        
        Returns:
            ConversationScenario configured for error handling
        """
        error_tool_request_id = f"error-{str(uuid.uuid4())[:8]}"
        return ConversationScenario(
            name="error_handling",
            description="Handling of tool execution errors"
        ).add_user_input(
            "Run an invalid command please"
        ).add_expected_llm_response(
            "I'll run that command for you.",
            tool_request={
                "request_id": error_tool_request_id,
                "tool_name": "executeBashCommand",
                "parameters": {"command": "invalid_command"}
            }
        ).add_tool_result(
            error_tool_request_id,
            "executeBashCommand",
            {"error_message": "Command not found: invalid_command"},
            status="error"
        ).add_expected_llm_response(
            "I encountered an error trying to run that command. The command 'invalid_command' was not found on the system."
        ).add_verification_step(
            lambda controller: assert_error_handled(controller, "Command not found"),
            "Verify error was properly handled"
        )


# Verification utility functions

def assert_message_count(controller, expected_count):
    """Assert that the message manager has the expected number of messages."""
    actual_count = len(controller.message_manager.messages)
    assert actual_count == expected_count, f"Expected {expected_count} messages, got {actual_count}"

def assert_tool_was_executed(controller, tool_name):
    """Assert that a specific tool was executed."""
    for call in controller.tool_request_handler.process_tool_request.call_args_list:
        args, kwargs = call
        tool_request = args[0] if args else kwargs.get("tool_request")
        if tool_request and tool_request.get("tool_name") == tool_name:
            return True
    assert False, f"Tool '{tool_name}' was not executed"

def assert_system_message_added(controller, message_content):
    """Assert that a specific system message was added."""
    for call in controller.message_manager.add_system_message.call_args_list:
        args, kwargs = call
        content = args[0] if args else kwargs.get("content")
        if content == message_content:
            return True
    assert False, f"System message '{message_content}' was not added"

def assert_error_handled(controller, error_text):
    """Assert that a specific error was handled."""
    for call in controller.error_handler.handle_error.call_args_list:
        args, kwargs = call
        if any(error_text in str(arg) for arg in args):
            return True
        if any(error_text in str(value) for value in kwargs.values()):
            return True
    assert False, f"Error containing '{error_text}' was not handled"


# Pytest fixtures

@pytest.fixture
def scenario_builder():
    """Provide a ScenarioBuilder instance for end-to-end tests."""
    return MockScenarioBuilder()

@pytest.fixture
def e2e_controller(framework_controller_factory):
    """Provide a pre-initialized controller for end-to-end tests."""
    controller = framework_controller_factory()
    controller.initialize()
    return controller

@pytest.fixture
def mock_conversation(mock_io_capture, mock_llm_adapter):
    """Set up a mock conversation environment for end-to-end tests."""
    def setup_conversation(controller, scenario):
        # Configure LLM adapter with scenario responses
        scenario.configure_mock_llm(mock_llm_adapter)
        
        # Configure TEPS with scenario tool results
        scenario.configure_mock_teps(controller.teps_manager.teps_instance)
        
        # Add user inputs to the input queue
        mock_io_capture.clear_inputs()
        for user_input in scenario.user_inputs:
            mock_io_capture.add_input(user_input)
        
        # Add a final /quit to end the conversation
        mock_io_capture.add_input("/quit")
        
        return controller
    
    return setup_conversation

@pytest.fixture
def e2e_test_data():
    """Provide test data for end-to-end tests."""
    # Paths to test data files
    test_data = {
        "python_file": "/path/to/example.py",
        "text_file": "/path/to/example.txt",
        "json_file": "/path/to/example.json",
        "project_dir": "/path/to/project"
    }
    
    # Content of test files
    test_file_contents = {
        "/path/to/example.py": "def hello_world():\n    print('Hello, world!')\n\nif __name__ == '__main__':\n    hello_world()",
        "/path/to/example.txt": "This is a sample text file for testing purposes.",
        "/path/to/example.json": json.dumps({"name": "Test Object", "values": [1, 2, 3], "active": True}, indent=2)
    }
    
    return {
        "paths": test_data,
        "contents": test_file_contents
    }

@pytest.fixture
def setup_pyfakefs_for_e2e(fs, e2e_test_data):
    """Set up a fake filesystem for end-to-end tests."""
    # Create directories
    fs.create_dir('/path/to')
    fs.create_dir('/path/to/project')
    
    # Create files with test content
    for file_path, content in e2e_test_data["contents"].items():
        fs.create_file(file_path, contents=content)
    
    return fs