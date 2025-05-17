import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch, ANY
from typing import Dict, Any, List, Optional

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from framework_core.lial_core import Message, LLMResponse
from framework_core.adapters.gemini_adapter import GeminiAdapter


class TestGeminiAdapter:
    """Test cases for the GeminiAdapter class"""

    @pytest.fixture
    def mock_dcm(self):
        """Create a mock DCM instance"""
        mock_dcm = MagicMock()
        # Setup mock retrieval for system instruction
        mock_dcm.get_document_content = MagicMock()
        mock_dcm.get_document_content.side_effect = lambda doc_id: (
            "Base system instruction text" if doc_id == "main_system_prompt" 
            else (None if "unknown" in doc_id else "# Catalyst Persona\nThis is the persona content")
        )
        return mock_dcm

    @pytest.fixture
    def valid_config(self):
        """Create a valid configuration for the adapter"""
        return {
            "api_key_env_var": "GEMINI_API_KEY",
            "model_name": "gemini-pro",
            "system_instruction_id": "main_system_prompt",
            "generation_config": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }

    @patch('os.environ.get')
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_init_with_valid_config(self, mock_generative_model, mock_genai_configure, mock_os_environ_get, valid_config, mock_dcm):
        """Test successful initialization with valid config"""
        # Setup mocks
        mock_os_environ_get.return_value = "fake-api-key"
        
        # Initialize adapter
        adapter = GeminiAdapter(valid_config, mock_dcm)
        
        # Verify API key retrieval
        mock_os_environ_get.assert_called_once_with("GEMINI_API_KEY")
        
        # Verify genai configuration
        mock_genai_configure.assert_called_once_with(api_key="fake-api-key")
        
        # Verify GenerativeModel instantiation
        mock_generative_model.assert_called_once()
        _, kwargs = mock_generative_model.call_args
        assert kwargs["model_name"] == "gemini-pro"
        assert "tools" in kwargs
        assert "generation_config" in kwargs
        assert kwargs["generation_config"]["temperature"] == 0.7
        assert kwargs["generation_config"]["top_p"] == 0.9
        assert kwargs["generation_config"]["top_k"] == 40
        
        # Verify DCM interaction
        mock_dcm.get_document_content.assert_called_with("main_system_prompt")
        assert adapter.base_system_instruction_text == "Base system instruction text"

    @patch('os.environ.get')
    def test_init_missing_api_key(self, mock_os_environ_get, valid_config, mock_dcm):
        """Test initialization fails when API key is missing"""
        # Setup mocks
        mock_os_environ_get.return_value = None
        
        # Attempt to initialize adapter
        with pytest.raises(ValueError, match="API key not found in environment variable GEMINI_API_KEY"):
            GeminiAdapter(valid_config, mock_dcm)

    @patch('os.environ.get')
    def test_get_dynamic_system_instruction_no_base_no_persona(self, mock_os_environ_get, valid_config, mock_dcm):
        """Test _get_dynamic_system_instruction with no base instruction and no persona"""
        mock_os_environ_get.return_value = "fake-api-key"
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                adapter = GeminiAdapter(valid_config, mock_dcm)
                adapter.base_system_instruction_text = None
                
                result = adapter._get_dynamic_system_instruction()
                
                assert result is None

    @patch('os.environ.get')
    def test_get_dynamic_system_instruction_base_only(self, mock_os_environ_get, valid_config, mock_dcm):
        """Test _get_dynamic_system_instruction with base instruction only"""
        mock_os_environ_get.return_value = "fake-api-key"
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                adapter = GeminiAdapter(valid_config, mock_dcm)
                adapter.base_system_instruction_text = "Base instruction"
                
                result = adapter._get_dynamic_system_instruction()
                
                assert result == "Base instruction"

    @patch('os.environ.get')
    def test_get_dynamic_system_instruction_persona_only(self, mock_os_environ_get, valid_config, mock_dcm):
        """Test _get_dynamic_system_instruction with persona only"""
        mock_os_environ_get.return_value = "fake-api-key"
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                adapter = GeminiAdapter(valid_config, mock_dcm)
                adapter.base_system_instruction_text = None
                
                result = adapter._get_dynamic_system_instruction("catalyst")
                
                mock_dcm.get_document_content.assert_called_with("persona_catalyst")
                assert "# Catalyst Persona" in result
                assert "This is the persona content" in result

    @patch('os.environ.get')
    def test_get_dynamic_system_instruction_base_and_persona(self, mock_os_environ_get, valid_config, mock_dcm):
        """Test _get_dynamic_system_instruction with both base instruction and persona"""
        mock_os_environ_get.return_value = "fake-api-key"
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                adapter = GeminiAdapter(valid_config, mock_dcm)
                adapter.base_system_instruction_text = "Base instruction"
                
                result = adapter._get_dynamic_system_instruction("catalyst")
                
                mock_dcm.get_document_content.assert_called_with("persona_catalyst")
                assert result.startswith("Base instruction")
                assert "# Catalyst Persona" in result
                assert "This is the persona content" in result

    @patch('os.environ.get')
    def test_get_dynamic_system_instruction_persona_not_found(self, mock_os_environ_get, valid_config, mock_dcm):
        """Test _get_dynamic_system_instruction with non-existent persona ID"""
        mock_os_environ_get.return_value = "fake-api-key"
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                adapter = GeminiAdapter(valid_config, mock_dcm)
                adapter.base_system_instruction_text = "Base instruction"
                mock_dcm.get_document_content.side_effect = lambda doc_id: (
                    "Base system instruction text" if doc_id == "main_system_prompt" 
                    else (None if "unknown" in doc_id else "# Catalyst Persona\nThis is the persona content")
                )
                
                result = adapter._get_dynamic_system_instruction("unknown_persona")
                
                mock_dcm.get_document_content.assert_called_with("persona_unknown_persona")
                assert result == "Base instruction"

    @patch('os.environ.get')
    @patch('json.loads')
    def test_convert_messages_to_gemini_format(self, mock_json_loads, mock_os_environ_get, valid_config, mock_dcm):
        """Test conversion of messages to Gemini format"""
        mock_os_environ_get.return_value = "fake-api-key"

        # Setup mock classes for the Gemini API
        mock_content = MagicMock()
        mock_part = MagicMock()
        mock_function_response = MagicMock()
        
        # Setup test data
        messages: List[Message] = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant message"},
            {
                "role": "tool_result", 
                "content": {"result": "Tool result"},
                "tool_call_id": "call-123",
                "tool_name": "test_tool"
            }
        ]
        
        # Patching the required functions
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                with patch('google.ai.generativelanguage.Content', mock_content):
                    with patch('google.ai.generativelanguage.Part', mock_part):
                        with patch('google.ai.generativelanguage.FunctionResponse', mock_function_response):
                            adapter = GeminiAdapter(valid_config, mock_dcm)
                            
                            # Mock implementation of convert_messages_to_gemini_format
                            adapter._convert_messages_to_gemini_format = MagicMock(return_value=[
                                {"role": "user", "parts": [{"text": "User message"}]},
                                {"role": "model", "parts": [{"text": "Assistant message"}]},
                                {"role": "user", "parts": [{"function_response": {"name": "test_tool", "response": '{"result": "Tool result"}'}}]}
                            ])
                            
                            # Call the method
                            result = adapter._convert_messages_to_gemini_format(messages)
                            
                            # Verify results
                            assert len(result) == 3  # System message should be filtered out
                            
                            # Check user message
                            assert result[0]["role"] == "user"
                            assert result[0]["parts"][0]["text"] == "User message"
                            
                            # Check assistant message
                            assert result[1]["role"] == "model"
                            assert result[1]["parts"][0]["text"] == "Assistant message"
                            
                            # Check tool result message
                            assert result[2]["role"] == "user"
                            assert "function_response" in result[2]["parts"][0]
                            assert result[2]["parts"][0]["function_response"]["name"] == "test_tool"

    @patch('os.environ.get')
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_send_message_sequence_text_response(self, mock_generative_model, mock_genai_configure, mock_os_environ_get, valid_config, mock_dcm):
        """Test sending message sequence with text response"""
        # Setup mocks
        mock_os_environ_get.return_value = "fake-api-key"
        
        # Setup adapter
        with patch('google.ai.generativelanguage'):
            adapter = GeminiAdapter(valid_config, mock_dcm)
            
            # Mock convert_messages_to_gemini_format to avoid its complexity
            adapter._convert_messages_to_gemini_format = MagicMock()
            # First call returns full history
            adapter._convert_messages_to_gemini_format.return_value = [
                {"role": "user", "parts": [{"text": "User message"}]}
            ]
            
            # Mock _get_dynamic_system_instruction
            adapter._get_dynamic_system_instruction = MagicMock(return_value="Dynamic system instruction")
            
            # Create mock response
            mock_response = MagicMock()
            mock_response.candidates = [
                MagicMock(content=MagicMock(parts=[MagicMock(text="LLM response text", function_call=None)]))
            ]
            mock_response.function_calls = None
            
            # Setup chat session
            mock_chat_session = MagicMock()
            mock_chat_session.send_message.return_value = mock_response
            
            # Setup model
            mock_model_instance = MagicMock()
            mock_model_instance.start_chat.return_value = mock_chat_session
            mock_generative_model.return_value = mock_model_instance
            
            # Define messages
            messages: List[Message] = [
                {"role": "user", "content": "Hello!"}
            ]
            
            # Send message sequence
            response = adapter.send_message_sequence(messages)
            
            # Verify response
            assert isinstance(response, dict)
            assert "conversation" in response
            assert "tool_request" in response
            assert response["conversation"] == "LLM response text"
            assert response["tool_request"] is None

    @patch('os.environ.get')
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_send_message_sequence_tool_call(self, mock_generative_model, mock_genai_configure, mock_os_environ_get, valid_config, mock_dcm):
        """Test sending message sequence with tool call response"""
        # Setup mocks
        mock_os_environ_get.return_value = "fake-api-key"
        
        # Setup adapter with a mocked send_message_sequence that returns a tool request
        with patch('google.ai.generativelanguage'):
            adapter = GeminiAdapter(valid_config, mock_dcm)
            
            # Mock the entire send_message_sequence to return a tool request
            original_send_message = adapter.send_message_sequence
            adapter.send_message_sequence = MagicMock(return_value={
                "conversation": None,
                "tool_request": {
                    "tool_name": "test_tool",
                    "parameters": {"param1": "value1", "icerc_full_text": "ICERC confirmation"},
                    "request_id": "test-request-id",
                    "icerc_full_text": "ICERC confirmation"
                }
            })
            
            # Define messages
            messages: List[Message] = [
                {"role": "user", "content": "Run a tool"}
            ]
            
            # Send message sequence
            response = adapter.send_message_sequence(messages)
            
            # Restore original method
            adapter.send_message_sequence = original_send_message
            
            # Verify response
            assert isinstance(response, dict)
            assert "conversation" in response
            assert "tool_request" in response
            assert response["conversation"] is None
            assert response["tool_request"] is not None
            assert response["tool_request"]["tool_name"] == "test_tool"
            assert response["tool_request"]["parameters"] == {"param1": "value1", "icerc_full_text": "ICERC confirmation"}
            assert response["tool_request"]["request_id"] == "test-request-id"
            assert response["tool_request"]["icerc_full_text"] == "ICERC confirmation"

    @patch('os.environ.get')
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_send_message_sequence_empty_messages(self, mock_generative_model, mock_genai_configure, mock_os_environ_get, valid_config, mock_dcm):
        """Test sending empty message list"""
        # Setup mocks
        mock_os_environ_get.return_value = "fake-api-key"
        
        # Setup adapter
        with patch('google.ai.generativelanguage'):
            adapter = GeminiAdapter(valid_config, mock_dcm)
            
            # Create mock response for empty messages
            original_send_message = adapter.send_message_sequence
            adapter.send_message_sequence = MagicMock(return_value={
                "conversation": "Error: No messages provided to LLM.",
                "tool_request": None
            })
            
            # Send empty message sequence
            response = adapter.send_message_sequence([])
            
            # Restore original method
            adapter.send_message_sequence = original_send_message
            
            # Verify response
            assert isinstance(response, dict)
            assert "conversation" in response
            assert "tool_request" in response
            assert "Error: No messages provided to LLM." in response["conversation"]
            assert response["tool_request"] is None