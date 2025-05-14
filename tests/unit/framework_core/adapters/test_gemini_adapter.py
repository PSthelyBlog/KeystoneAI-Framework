import os
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional

from framework_core.lial_core import Message, LLMResponse
from framework_core.adapters.gemini_adapter import GeminiAdapter

# Mock DCM class for testing
class MockDCM:
    def get_document_content(self, doc_id: str) -> Optional[str]:
        if doc_id == "system_instruction":
            return "You are an AI assistant."
        elif doc_id == "persona_catalyst":
            return "You are Catalyst, a strategic AI assistant."
        elif doc_id == "persona_forge":
            return "You are Forge, an implementation AI assistant."
        return None

# Mock response classes to simulate Gemini API responses
class MockPart:
    def __init__(self, text=None, function_call=None):
        self.text = text
        self.function_call = function_call

class MockFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class MockContent:
    def __init__(self, parts):
        self.parts = parts

class MockCandidate:
    def __init__(self, content):
        self.content = content

class MockGeminiResponse:
    def __init__(self, candidates):
        self.candidates = candidates

@pytest.fixture
def mock_env_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key-for-testing")

@pytest.fixture
def mock_dcm():
    return MockDCM()

@pytest.fixture
def basic_config():
    return {
        "api_key_env_var": "GEMINI_API_KEY",
        "model_name": "gemini-1.5-pro-latest",
        "system_instruction_id": "system_instruction"
    }

class TestGeminiAdapter:
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_initialization(self, mock_configure, mock_generative_model, mock_env_api_key, mock_dcm, basic_config):
        # Test that the adapter initializes correctly
        adapter = GeminiAdapter(config=basic_config, dcm_instance=mock_dcm)
        
        # Verify that the API was configured with the correct key
        mock_configure.assert_called_once_with(api_key="fake-api-key-for-testing")
        
        # Verify that the generative model was created with correct parameters
        mock_generative_model.assert_called_once()
        assert adapter.model_name == "gemini-1.5-pro-latest"
        assert adapter.system_instruction == "You are an AI assistant."
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_convert_messages_to_gemini_format(self, mock_configure, mock_generative_model, 
                                              mock_env_api_key, mock_dcm, basic_config):
        adapter = GeminiAdapter(config=basic_config, dcm_instance=mock_dcm)
        
        # Test converting a simple user message
        messages = [{"role": "user", "content": "Hello"}]
        gemini_messages = adapter._convert_messages_to_gemini_format(messages)
        
        # Should have 2 messages: system instruction and user message
        assert len(gemini_messages) == 2
        assert gemini_messages[0]["role"] == "system"
        assert gemini_messages[0]["parts"][0]["text"] == "You are an AI assistant."
        assert gemini_messages[1]["role"] == "user"
        assert gemini_messages[1]["parts"][0]["text"] == "Hello"
        
        # Test with active persona
        gemini_messages = adapter._convert_messages_to_gemini_format(messages, active_persona_id="catalyst")
        assert "You are Catalyst" in gemini_messages[0]["parts"][0]["text"]
        
        # Test with tool result message
        tool_messages = [
            {"role": "user", "content": "Run ls"},
            {"role": "assistant", "content": "I'll run that for you"},
            {"role": "tool_result", "content": "file1.txt\nfile2.txt", "tool_name": "executeBashCommand", "tool_call_id": "cmd-123"}
        ]
        gemini_messages = adapter._convert_messages_to_gemini_format(tool_messages)
        assert len(gemini_messages) == 4  # system + 3 messages
        assert gemini_messages[3]["role"] == "tool"
        assert "executeBashCommand" in str(gemini_messages[3])
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_send_message_sequence_text_only(self, mock_configure, mock_generative_model_class, 
                                            mock_env_api_key, mock_dcm, basic_config):
        # Create a mock for the GenerativeModel instance
        mock_generative_model = mock_generative_model_class.return_value
        
        # Set up the mock to return a text-only response
        mock_content = MockContent(parts=[MockPart(text="I'm a helpful assistant.")])
        mock_candidate = MockCandidate(content=mock_content)
        mock_response = MockGeminiResponse(candidates=[mock_candidate])
        mock_generative_model.generate_content.return_value = mock_response
        
        # Create the adapter and test sending a message
        adapter = GeminiAdapter(config=basic_config, dcm_instance=mock_dcm)
        response = adapter.send_message_sequence([{"role": "user", "content": "Hello"}])
        
        # Verify the response structure
        assert isinstance(response, dict)
        assert "conversation" in response
        assert "tool_request" in response
        assert response["conversation"] == "I'm a helpful assistant."
        assert response["tool_request"] is None
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_send_message_sequence_with_tool_call(self, mock_configure, mock_generative_model_class, 
                                                 mock_env_api_key, mock_dcm, basic_config):
        # Create a mock for the GenerativeModel instance
        mock_generative_model = mock_generative_model_class.return_value
        
        # Set up the mock to return a response with a function call
        function_call = MockFunctionCall(
            name="executeBashCommand",
            args={
                "command": "ls -la",
                "working_directory": "/home",
                "icerc_full_text": "Intent: List all files\nCommand: ls -la\nExpected: Directory listing\nRisk: Low"
            }
        )
        mock_content = MockContent(parts=[
            MockPart(text="I'll run that command for you."),
            MockPart(function_call=function_call)
        ])
        mock_candidate = MockCandidate(content=mock_content)
        mock_response = MockGeminiResponse(candidates=[mock_candidate])
        mock_generative_model.generate_content.return_value = mock_response
        
        # Create the adapter and test sending a message
        adapter = GeminiAdapter(config=basic_config, dcm_instance=mock_dcm)
        response = adapter.send_message_sequence([{"role": "user", "content": "Run ls -la"}])
        
        # Verify the response structure
        assert isinstance(response, dict)
        assert "conversation" in response
        assert "tool_request" in response
        assert response["conversation"] == "I'll run that command for you."
        assert response["tool_request"] is not None
        assert response["tool_request"]["tool_name"] == "executeBashCommand"
        assert response["tool_request"]["parameters"]["command"] == "ls -la"
        assert "icerc_full_text" in response["tool_request"]["parameters"]
        assert "Intent: List all files" in response["tool_request"]["icerc_full_text"]
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_send_message_sequence_error_handling(self, mock_configure, mock_generative_model_class, 
                                                mock_env_api_key, mock_dcm, basic_config):
        # Create a mock for the GenerativeModel instance
        mock_generative_model = mock_generative_model_class.return_value
        
        # Set up the mock to raise an exception
        mock_generative_model.generate_content.side_effect = Exception("API error")
        
        # Create the adapter and test sending a message
        adapter = GeminiAdapter(config=basic_config, dcm_instance=mock_dcm)
        response = adapter.send_message_sequence([{"role": "user", "content": "Hello"}])
        
        # Verify the error response
        assert "Error communicating with Gemini API" in response["conversation"]
        assert response["tool_request"] is None
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_missing_icerc_text(self, mock_configure, mock_generative_model_class, 
                               mock_env_api_key, mock_dcm, basic_config):
        # Create a mock for the GenerativeModel instance
        mock_generative_model = mock_generative_model_class.return_value
        
        # Set up the mock to return a response with a function call missing icerc_full_text
        function_call = MockFunctionCall(
            name="executeBashCommand",
            args={
                "command": "ls -la",
                "working_directory": "/home"
                # Missing icerc_full_text
            }
        )
        mock_content = MockContent(parts=[
            MockPart(text="Running command"),
            MockPart(function_call=function_call)
        ])
        mock_candidate = MockCandidate(content=mock_content)
        mock_response = MockGeminiResponse(candidates=[mock_candidate])
        mock_generative_model.generate_content.return_value = mock_response
        
        # Create the adapter and test sending a message
        adapter = GeminiAdapter(config=basic_config, dcm_instance=mock_dcm)
        response = adapter.send_message_sequence([{"role": "user", "content": "Run ls -la"}])
        
        # Verify the warning is added to icerc_full_text
        assert "Warning: Missing ICERC protocol text" in response["tool_request"]["icerc_full_text"]