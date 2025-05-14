import pytest
from typing import Dict, List, Optional, Any

from framework_core.lial_core import (
    LLMAdapterInterface,
    Message,
    ToolRequest,
    LLMResponse,
    ToolResult
)

# Define a minimal concrete implementation for testing
class MockLLMAdapter(LLMAdapterInterface):
    def __init__(self, config: Dict[str, Any], dcm_instance: Any) -> None:
        self.config = config
        self.dcm_instance = dcm_instance
    
    def send_message_sequence(
        self, 
        messages: List[Message], 
        active_persona_id: Optional[str] = None
    ) -> LLMResponse:
        return {
            "conversation": "Mock LLM response",
            "tool_request": None
        }

class TestLIALCore:
    def test_message_structure(self):
        # Test creating a valid Message object
        message: Message = {
            "role": "user",
            "content": "Hello, LLM!"
        }
        assert message["role"] == "user"
        assert message["content"] == "Hello, LLM!"
        
        # Test with optional fields
        tool_message: Message = {
            "role": "tool_result",
            "content": "Command executed successfully",
            "tool_call_id": "cmd-123",
            "tool_name": "bash"
        }
        assert tool_message["tool_call_id"] == "cmd-123"
        assert tool_message["tool_name"] == "bash"
    
    def test_tool_request_structure(self):
        # Test creating a valid ToolRequest
        tool_req: ToolRequest = {
            "request_id": "req-456",
            "tool_name": "bash",
            "parameters": {
                "command": "ls -la",
                "working_directory": "/home/user"
            },
            "icerc_full_text": "Intent: List files...\nCommand: ls -la\nExpected: Show files\nRisk: Low"
        }
        
        assert tool_req["request_id"] == "req-456"
        assert tool_req["tool_name"] == "bash"
        assert tool_req["parameters"]["command"] == "ls -la"
        assert "icerc_full_text" in tool_req
    
    def test_llm_response_structure(self):
        # Test a response with just conversation
        response1: LLMResponse = {
            "conversation": "Hello, I'm an LLM!",
            "tool_request": None
        }
        assert response1["conversation"] == "Hello, I'm an LLM!"
        assert response1["tool_request"] is None
        
        # Test a response with a tool request
        response2: LLMResponse = {
            "conversation": "I'll execute that command for you.",
            "tool_request": {
                "request_id": "cmd-789",
                "tool_name": "bash",
                "parameters": {"command": "echo hello"},
                "icerc_full_text": "Intent: Echo text...\nCommand: echo hello\nExpected: Print hello\nRisk: Low"
            }
        }
        assert response2["conversation"] == "I'll execute that command for you."
        assert response2["tool_request"]["tool_name"] == "bash"
    
    def test_tool_result_structure(self):
        # Test a successful tool execution result
        result: ToolResult = {
            "request_id": "cmd-789",
            "tool_name": "bash",
            "status": "success",
            "data": {
                "stdout": "hello\n",
                "stderr": "",
                "exit_code": 0
            }
        }
        assert result["status"] == "success"
        assert result["data"]["stdout"] == "hello\n"
    
    def test_mock_adapter_implementation(self):
        # Test that we can create a concrete implementation
        adapter = MockLLMAdapter(
            config={"api_key_env_var": "TEST_API_KEY"}, 
            dcm_instance=None
        )
        
        # Test sending messages
        response = adapter.send_message_sequence(
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        assert isinstance(response, dict)
        assert "conversation" in response
        assert response["conversation"] == "Mock LLM response"