import pytest
from typing import Dict, Any, Optional, List
import sys
import os
from unittest.mock import MagicMock

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from framework_core.lial_core import Message, ToolRequest, LLMResponse, ToolResult, LLMAdapterInterface


class TestTypedDicts:
    """Test cases for the TypedDict structures defined in lial_core.py"""

    def test_message_structure(self):
        """Test that Message TypedDict can be created correctly"""
        # Test with required fields only
        message: Message = {
            "role": "user",
            "content": "Hello, world!"
        }
        assert message["role"] == "user"
        assert message["content"] == "Hello, world!"
        assert "tool_call_id" not in message
        assert "tool_name" not in message

        # Test with optional fields
        message_with_tool: Message = {
            "role": "tool_result",
            "content": "Tool result here",
            "tool_call_id": "12345",
            "tool_name": "test_tool"
        }
        assert message_with_tool["role"] == "tool_result"
        assert message_with_tool["content"] == "Tool result here"
        assert message_with_tool["tool_call_id"] == "12345"
        assert message_with_tool["tool_name"] == "test_tool"

        # Test with various roles
        for role in ["user", "assistant", "system", "tool_result"]:
            message = {"role": role, "content": "Test content"}
            assert message["role"] == role

    def test_tool_request_structure(self):
        """Test that ToolRequest TypedDict can be created correctly"""
        tool_request: ToolRequest = {
            "tool_name": "test_tool",
            "parameters": {"param1": "value1", "param2": "value2"},
            "request_id": "req-12345",
            "icerc_full_text": "ICERC Protocol confirmation text here"
        }
        
        assert tool_request["tool_name"] == "test_tool"
        assert tool_request["parameters"] == {"param1": "value1", "param2": "value2"}
        assert tool_request["request_id"] == "req-12345"
        assert tool_request["icerc_full_text"] == "ICERC Protocol confirmation text here"

    def test_tool_result_structure(self):
        """Test that ToolResult TypedDict can be created correctly"""
        tool_result: ToolResult = {
            "tool_name": "test_tool",
            "content": "Result of the tool execution",
            "tool_call_id": "call-12345"
        }
        
        assert tool_result["tool_name"] == "test_tool"
        assert tool_result["content"] == "Result of the tool execution"
        assert tool_result["tool_call_id"] == "call-12345"

    def test_llm_response_structure(self):
        """Test that LLMResponse TypedDict can be created correctly"""
        # Test text-only response
        text_response: LLMResponse = {
            "text": "This is a text response",
            "error": None,
            "tool_requests": None
        }
        
        assert text_response["text"] == "This is a text response"
        assert text_response["error"] is None
        assert text_response["tool_requests"] is None

        # Test tool request response
        tool_request: ToolRequest = {
            "tool_name": "test_tool",
            "parameters": {"param1": "value1"},
            "request_id": "req-12345",
            "icerc_full_text": "ICERC confirmation"
        }
        
        tool_response: LLMResponse = {
            "text": None,
            "error": None,
            "tool_requests": [tool_request]
        }
        
        assert tool_response["text"] is None
        assert tool_response["error"] is None
        assert len(tool_response["tool_requests"]) == 1
        assert tool_response["tool_requests"][0] == tool_request

        # Test error response
        error_response: LLMResponse = {
            "text": None,
            "error": "API Error occurred",
            "tool_requests": None
        }
        
        assert error_response["text"] is None
        assert error_response["error"] == "API Error occurred"
        assert error_response["tool_requests"] is None


class TestLLMAdapterInterface:
    """Test cases for the LLMAdapterInterface abstract base class"""

    def test_abstract_class_instantiation(self):
        """Test that LLMAdapterInterface cannot be instantiated directly"""
        with pytest.raises(TypeError):
            LLMAdapterInterface({}, None)

    def test_concrete_implementation(self):
        """Test a concrete implementation of LLMAdapterInterface"""
        class ConcreteAdapter(LLMAdapterInterface):
            def __init__(self, config: Dict[str, Any], dcm_instance: Optional[Any] = None):
                self.config = config
                self.dcm_instance = dcm_instance
            
            def send_message_sequence(self, messages: List[Message], active_persona_id: Optional[str] = None) -> LLMResponse:
                # Simple implementation for testing
                return {
                    "text": "Response from concrete adapter",
                    "error": None,
                    "tool_requests": None
                }
        
        # Test instantiation
        config = {"test_key": "test_value"}
        dcm_instance = MagicMock()
        adapter = ConcreteAdapter(config, dcm_instance)
        
        assert adapter.config == config
        assert adapter.dcm_instance == dcm_instance
        
        # Test send_message_sequence
        messages: List[Message] = [
            {"role": "user", "content": "Hello!"}
        ]
        
        response = adapter.send_message_sequence(messages)
        assert response["text"] == "Response from concrete adapter"
        assert response["error"] is None
        assert response["tool_requests"] is None