"""
Utility classes and functions for integration testing.

This module provides utility classes and functions used in the integration tests
for the KeystoneAI-Framework, including:
- MockLLMAdapter: A configurable mock LLM adapter
- ResponseBuilder: A utility for constructing test responses
- MockInput/OutputCapture: Utilities for terminal I/O mocking
"""

import io
import sys
from typing import Dict, List, Optional, Any, Callable, Union
from unittest.mock import MagicMock

from framework_core.lial_core import LLMAdapterInterface, Message, LLMResponse, ToolRequest

class MockLLMAdapter(LLMAdapterInterface):
    """
    A configurable mock LLM adapter for testing.
    
    This adapter implements the LLMAdapterInterface and can be configured to
    return predetermined responses based on input patterns, active persona,
    or specific test scenarios.
    """
    
    def __init__(self, config: Dict[str, Any], dcm_instance: Any) -> None:
        """
        Initialize the mock LLM adapter.
        
        Args:
            config: Configuration dictionary with settings
            dcm_instance: Dynamic Context Manager instance for context access
        """
        self.config = config
        self.dcm_instance = dcm_instance
        
        # Default responses
        self.responses = {
            "default": {
                "conversation": "I am an AI assistant. How can I help you today?",
                "tool_request": None
            }
        }
        
        # Response patterns - can be configured per test
        self.patterns = {}
        
        # Persona-specific responses
        self.persona_responses = {
            "catalyst": {
                "conversation": "(Catalyst) I'll help you plan and architect a solution.",
                "tool_request": None
            },
            "forge": {
                "conversation": "(Forge) I'll implement that for you with precision.",
                "tool_request": None
            }
        }
        
        # Error simulations
        self.error_responses = {
            "api_error": Exception("API Error"),
            "timeout": TimeoutError("Request timed out"),
            "malformed": {"invalid": "format"}
        }
        
        # Tracking for test verification
        self.call_history = []
        self.call_count = 0
    
    def configure_response(self, key: str, response: Dict[str, Any]) -> None:
        """
        Configure a specific response for a key.
        
        Args:
            key: The response key
            response: The response dictionary
        """
        self.responses[key] = response
    
    def configure_pattern(self, pattern: str, response_key: str) -> None:
        """
        Configure a pattern to match in messages.
        
        Args:
            pattern: String pattern to match in message content
            response_key: Key of the response to return when pattern matches
        """
        self.patterns[pattern] = response_key
    
    def configure_error(self, key: str, error: Exception) -> None:
        """
        Configure an error response.
        
        Args:
            key: The error key
            error: The exception to raise
        """
        self.error_responses[key] = error
    
    def clear_configurations(self) -> None:
        """Clear all configured responses and patterns."""
        self.responses = {"default": self.responses["default"]}
        self.patterns = {}
        self.call_history = []
        self.call_count = 0
    
    def _find_matching_response(self, messages: List[Message], active_persona_id: Optional[str]) -> Dict[str, Any]:
        """
        Find the appropriate response based on message content and active persona.
        
        Args:
            messages: List of messages to analyze
            active_persona_id: Optional ID of the active persona
            
        Returns:
            The appropriate response dictionary
        """
        # Check for pattern matches in the last user message
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        if last_user_message:
            for pattern, response_key in self.patterns.items():
                if pattern.lower() in last_user_message.lower():
                    return self.responses.get(response_key, self.responses["default"])
        
        # Check for persona-specific response
        if active_persona_id and active_persona_id in self.persona_responses:
            return self.persona_responses[active_persona_id]
        
        # Default response
        return self.responses["default"]
    
    def send_message_sequence(
        self, 
        messages: List[Message], 
        active_persona_id: Optional[str] = None
    ) -> LLMResponse:
        """
        Send a sequence of messages and get a mock response.
        
        Args:
            messages: List of Message objects
            active_persona_id: Optional ID of the active persona
            
        Returns:
            LLMResponse containing conversational text and optional tool request
            
        Raises:
            Exception: If configured to simulate an error
        """
        # Track call for testing verification
        self.call_count += 1
        self.call_history.append({
            "messages": messages.copy(),
            "active_persona_id": active_persona_id
        })
        
        # Check for error simulation keys in the last user message
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        if last_user_message:
            for error_key, error in self.error_responses.items():
                if error_key in last_user_message.lower():
                    if isinstance(error, Exception):
                        raise error
                    return error
        
        # Find and return the appropriate response
        return self._find_matching_response(messages, active_persona_id)


class ResponseBuilder:
    """
    Utility class for building test response structures.
    
    This class provides methods for constructing valid response objects for
    different test scenarios, following the structure expected by the framework.
    """
    
    @staticmethod
    def conversation(text: str) -> LLMResponse:
        """
        Build a simple conversation response.
        
        Args:
            text: The conversation text
            
        Returns:
            LLMResponse with only conversation text
        """
        return {
            "conversation": text,
            "tool_request": None
        }
    
    @staticmethod
    def tool_request(
        tool_name: str, 
        parameters: Dict[str, Any], 
        conversation_text: Optional[str] = None,
        request_id: Optional[str] = None,
        icerc_text: Optional[str] = None
    ) -> LLMResponse:
        """
        Build a response containing a tool request.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool execution
            conversation_text: Optional conversation text
            request_id: Optional request ID (generated if not provided)
            icerc_text: Optional ICERC protocol text
            
        Returns:
            LLMResponse with conversation text and tool request
        """
        # Generate request ID if not provided
        if not request_id:
            import uuid
            request_id = f"req-{str(uuid.uuid4())[:8]}"
        
        # Generate ICERC text if not provided
        if not icerc_text:
            param_str = ", ".join([f"{k}={v}" for k, v in parameters.items()])
            icerc_text = (
                f"Intent: Execute {tool_name}\n"
                f"Command: {tool_name}({param_str})\n"
                f"Expected: Tool will return results\n"
                f"Risk: Tool execution may have side effects\n"
                f"Confirmation: Please confirm [Y/N]"
            )
        
        # Build tool request
        tool_request: ToolRequest = {
            "request_id": request_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "icerc_full_text": icerc_text
        }
        
        # Return LLMResponse
        return {
            "conversation": conversation_text or f"I'll use the {tool_name} tool to help with that.",
            "tool_request": tool_request
        }
    
    @staticmethod
    def error_response(error_message: str) -> LLMResponse:
        """
        Build an error response.
        
        Args:
            error_message: The error message
            
        Returns:
            LLMResponse indicating an error
        """
        return {
            "conversation": f"I encountered an error: {error_message}",
            "tool_request": None
        }
    
    @staticmethod
    def message_sequence(roles_and_contents: List[tuple]) -> List[Message]:
        """
        Build a sequence of messages.
        
        Args:
            roles_and_contents: List of (role, content) tuples
            
        Returns:
            List of Message objects
        """
        messages = []
        
        for role, content in roles_and_contents:
            if role == "tool_result":
                # For tool_result, content should be a tuple (content, tool_name, tool_call_id)
                tool_content, tool_name, tool_call_id = content
                messages.append({
                    "role": role,
                    "content": tool_content,
                    "tool_name": tool_name,
                    "tool_call_id": tool_call_id
                })
            else:
                messages.append({
                    "role": role,
                    "content": content
                })
        
        return messages


class MockIOCapture:
    """
    Utility for capturing and simulating terminal I/O.
    
    This class provides methods for:
    - Capturing stdout/stderr output
    - Simulating user input
    - Verifying output formatting
    """
    
    def __init__(self):
        """Initialize the IO capture utility."""
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
        self.input_queue = []
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.original_input = input
    
    def start_capture(self) -> None:
        """Start capturing stdout and stderr."""
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
    
    def stop_capture(self) -> None:
        """Stop capturing and restore original stdout and stderr."""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
    
    def add_input(self, *inputs: str) -> None:
        """
        Add inputs to the queue for simulation.
        
        Args:
            *inputs: Input strings to queue
        """
        self.input_queue.extend(inputs)
    
    def mock_input(self, prompt: str = "") -> str:
        """
        Mock the input function.
        
        Args:
            prompt: Input prompt (will be printed)
            
        Returns:
            Next input from the queue
        """
        print(prompt, end="")
        
        if not self.input_queue:
            return ""
        
        return self.input_queue.pop(0)
    
    def patch_input(self) -> None:
        """Patch the built-in input function with our mock."""
        __builtins__["input"] = self.mock_input
    
    def restore_input(self) -> None:
        """Restore the original input function."""
        __builtins__["input"] = self.original_input
    
    def get_stdout(self) -> str:
        """
        Get the captured stdout content.
        
        Returns:
            Captured stdout as string
        """
        return self.stdout_capture.getvalue()
    
    def get_stderr(self) -> str:
        """
        Get the captured stderr content.
        
        Returns:
            Captured stderr as string
        """
        return self.stderr_capture.getvalue()
    
    def clear_captures(self) -> None:
        """Clear the captured stdout and stderr."""
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
    
    def clear_inputs(self) -> None:
        """Clear the input queue."""
        self.input_queue = []
    
    def reset(self) -> None:
        """Reset the IO capture to its initial state."""
        self.stop_capture()
        self.restore_input()
        self.clear_captures()
        self.clear_inputs()
        self.start_capture()
        self.patch_input()
    
    def verify_contains(self, text: str, case_sensitive: bool = True) -> bool:
        """
        Verify if the captured stdout contains specified text.
        
        Args:
            text: Text to search for
            case_sensitive: Whether the search is case-sensitive
            
        Returns:
            True if the text is found, False otherwise
        """
        stdout = self.get_stdout()
        
        if not case_sensitive:
            return text.lower() in stdout.lower()
        
        return text in stdout
    
    def verify_matches(self, pattern: str) -> bool:
        """
        Verify if the captured stdout matches a regex pattern.
        
        Args:
            pattern: Regular expression pattern
            
        Returns:
            True if the pattern matches, False otherwise
        """
        import re
        stdout = self.get_stdout()
        return bool(re.search(pattern, stdout))


class IntegrationTestCase:
    """
    Base class for integration tests with common setup and assertions.
    
    This class provides:
    - Common fixture setup
    - Standard assertions for integration testing
    - Helper methods for test configuration
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create mock I/O capture
        self.io_capture = MockIOCapture()
        
        # Create response builder
        self.response_builder = ResponseBuilder
        
        # Tracked mocks to verify
        self.mocks = {}
    
    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        # Clean up I/O capture
        if hasattr(self, 'io_capture'):
            self.io_capture.reset()
    
    def create_mock_llm_adapter(self, config: Dict[str, Any] = None, dcm_instance: Any = None) -> MockLLMAdapter:
        """
        Create a mock LLM adapter.
        
        Args:
            config: Optional configuration dictionary
            dcm_instance: Optional DCM instance
            
        Returns:
            Configured MockLLMAdapter
        """
        default_config = {
            "model_name": "mock-llm",
            "temperature": 0.7,
            "api_key_env_var": "MOCK_API_KEY"
        }
        
        adapter = MockLLMAdapter(
            config or default_config,
            dcm_instance or MagicMock()
        )
        
        return adapter
    
    def create_mock_component(self, name: str, **kwargs) -> MagicMock:
        """
        Create and track a mock component.
        
        Args:
            name: Name of the component to mock
            **kwargs: Additional attributes for the mock
            
        Returns:
            Configured MagicMock
        """
        mock = MagicMock(name=name, **kwargs)
        self.mocks[name] = mock
        return mock
    
    def assert_interaction_flow(self, component: Any, expected_methods: List[tuple]) -> None:
        """
        Assert that component methods were called in the expected sequence.
        
        Args:
            component: The component with recorded method calls
            expected_methods: List of (method_name, args, kwargs) tuples
        """
        actual_calls = component.method_calls
        
        # Check that we have the right number of calls
        assert len(actual_calls) >= len(expected_methods), (
            f"Expected at least {len(expected_methods)} method calls, got {len(actual_calls)}"
        )
        
        # Check each expected method call
        for i, (method_name, args, kwargs) in enumerate(expected_methods):
            actual_method, actual_args, actual_kwargs = actual_calls[i]
            
            assert actual_method == method_name, (
                f"Expected method #{i} to be {method_name}, got {actual_method}"
            )
            
            # Check args and kwargs if provided
            if args:
                assert actual_args == args, (
                    f"Expected args for {method_name} to be {args}, got {actual_args}"
                )
            
            if kwargs:
                assert actual_kwargs == kwargs, (
                    f"Expected kwargs for {method_name} to be {kwargs}, got {actual_kwargs}"
                )
    
    def assert_component_state(self, component: Any, **expected_attributes) -> None:
        """
        Assert that a component has the expected attribute values.
        
        Args:
            component: The component to check
            **expected_attributes: Expected attribute values
        """
        for attr_name, expected_value in expected_attributes.items():
            assert hasattr(component, attr_name), (
                f"Component {component.__class__.__name__} missing attribute {attr_name}"
            )
            
            actual_value = getattr(component, attr_name)
            assert actual_value == expected_value, (
                f"Expected {component.__class__.__name__}.{attr_name} to be {expected_value}, "
                f"got {actual_value}"
            )
    
    def assert_output_contains(self, text: str, case_sensitive: bool = True) -> None:
        """
        Assert that the captured output contains the specified text.
        
        Args:
            text: Text to search for
            case_sensitive: Whether the search is case-sensitive
        """
        assert self.io_capture.verify_contains(text, case_sensitive), (
            f"Expected output to contain '{text}', but it doesn't.\n"
            f"Actual output: {self.io_capture.get_stdout()}"
        )
    
    def assert_output_matches(self, pattern: str) -> None:
        """
        Assert that the captured output matches the regex pattern.
        
        Args:
            pattern: Regular expression pattern
        """
        assert self.io_capture.verify_matches(pattern), (
            f"Expected output to match pattern '{pattern}', but it doesn't.\n"
            f"Actual output: {self.io_capture.get_stdout()}"
        )
    
    def assert_no_errors(self) -> None:
        """Assert that no errors were logged to stderr."""
        stderr = self.io_capture.get_stderr()
        assert not stderr.strip(), f"Unexpected errors in stderr: {stderr}"
    
    def assert_error_contains(self, text: str) -> None:
        """
        Assert that the captured stderr contains the specified text.
        
        Args:
            text: Text to search for
        """
        stderr = self.io_capture.get_stderr()
        assert text in stderr, (
            f"Expected stderr to contain '{text}', but it doesn't.\n"
            f"Actual stderr: {stderr}"
        )