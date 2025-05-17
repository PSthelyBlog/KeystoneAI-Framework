import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from framework_core.component_managers.lial_manager import LIALManager
from framework_core.adapters.gemini_adapter import GeminiAdapter
from framework_core.lial_core import Message, LLMResponse
from framework_core.exceptions import LIALInitError, ConfigError


class TestLIALManager:
    """Test cases for the LIALManager class"""

    @pytest.fixture
    def mock_dcm_manager(self):
        """Create a mock DCM manager"""
        mock_manager = MagicMock()
        mock_manager.dcm_instance = MagicMock()
        return mock_manager

    @pytest.fixture
    def valid_config(self):
        """Create a valid configuration for the LIAL manager"""
        return {
            "llm_provider": "gemini",
            "llm_settings": {
                "api_key_env_var": "GEMINI_API_KEY",
                "model_name": "gemini-pro",
                "system_instruction_id": "main_system_prompt",
                "temperature": 0.7
            }
        }

    def test_init(self, valid_config, mock_dcm_manager):
        """Test initialization of LIALManager"""
        llm_provider = valid_config["llm_provider"]
        llm_settings = valid_config["llm_settings"]
        
        manager = LIALManager(llm_provider, llm_settings, mock_dcm_manager)
        
        assert manager.llm_provider == "gemini"
        assert manager.llm_settings == llm_settings
        assert manager.dcm_manager == mock_dcm_manager
        assert manager.adapter_instance is None

    @patch('framework_core.adapters.gemini_adapter.GeminiAdapter')
    def test_initialize_with_gemini(self, mock_gemini_adapter_class, valid_config, mock_dcm_manager):
        """Test successful initialization with Gemini provider"""
        llm_provider = valid_config["llm_provider"]
        llm_settings = valid_config["llm_settings"]
        
        # Create a mock adapter instance that will be returned by the class constructor
        mock_adapter_instance = MagicMock()
        mock_gemini_adapter_class.return_value = mock_adapter_instance
        
        manager = LIALManager(llm_provider, llm_settings, mock_dcm_manager)
        manager.initialize()
        
        # Verify adapter creation
        mock_gemini_adapter_class.assert_called_once_with(
            config=llm_settings, 
            dcm_instance=mock_dcm_manager.dcm_instance
        )
        assert manager.adapter_instance is mock_adapter_instance

    def test_initialize_with_invalid_provider(self, mock_dcm_manager):
        """Test initialization with unsupported provider"""
        llm_provider = "unsupported_provider"
        llm_settings = {"some_setting": "value"}
        
        manager = LIALManager(llm_provider, llm_settings, mock_dcm_manager)
        
        with pytest.raises(LIALInitError, match=f"Unsupported LLM provider: {llm_provider}"):
            manager.initialize()

    def test_initialize_with_empty_provider(self, mock_dcm_manager):
        """Test initialization with empty provider"""
        llm_provider = ""
        llm_settings = {"some_setting": "value"}
        
        manager = LIALManager(llm_provider, llm_settings, mock_dcm_manager)
        
        with pytest.raises(ConfigError, match="LLM provider is required for LIAL initialization"):
            manager.initialize()

    def test_initialize_with_none_provider(self, mock_dcm_manager):
        """Test initialization with None provider"""
        llm_provider = None
        llm_settings = {"some_setting": "value"}
        
        manager = LIALManager(llm_provider, llm_settings, mock_dcm_manager)
        
        with pytest.raises(ConfigError, match="LLM provider is required for LIAL initialization"):
            manager.initialize()

    @patch('framework_core.adapters.gemini_adapter.GeminiAdapter')
    def test_initialize_with_adapter_error(self, mock_gemini_adapter_class, valid_config, mock_dcm_manager):
        """Test initialization handling adapter instantiation error"""
        llm_provider = valid_config["llm_provider"]
        llm_settings = valid_config["llm_settings"]
        
        # Make adapter raise exception
        mock_gemini_adapter_class.side_effect = ValueError("API key not found")
        
        manager = LIALManager(llm_provider, llm_settings, mock_dcm_manager)
        
        with pytest.raises(LIALInitError, match="Failed to initialize LIAL: API key not found"):
            manager.initialize()

    @patch('framework_core.adapters.gemini_adapter.GeminiAdapter')
    def test_send_messages_success(self, mock_gemini_adapter_class, valid_config, mock_dcm_manager):
        """Test successful sending of messages"""
        llm_provider = valid_config["llm_provider"]
        llm_settings = valid_config["llm_settings"]
        
        # Create mock adapter instance
        mock_adapter_instance = MagicMock()
        expected_response: LLMResponse = {
            "conversation": "Response from LLM",
            "tool_request": None
        }
        mock_adapter_instance.send_message_sequence.return_value = expected_response
        mock_gemini_adapter_class.return_value = mock_adapter_instance
        
        # Setup manager with mock adapter
        manager = LIALManager(llm_provider, llm_settings, mock_dcm_manager)
        manager.initialize()
        
        # Send messages
        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": "Hello!"}
        ]
        active_persona_id = "catalyst"
        
        response = manager.send_messages(messages, active_persona_id)
        
        # Verify adapter call
        mock_adapter_instance.send_message_sequence.assert_called_once_with(messages, active_persona_id=active_persona_id)
        assert response == expected_response

    def test_send_messages_without_initialization(self, valid_config, mock_dcm_manager):
        """Test sending messages without initializing adapter"""
        llm_provider = valid_config["llm_provider"]
        llm_settings = valid_config["llm_settings"]
        
        manager = LIALManager(llm_provider, llm_settings, mock_dcm_manager)
        # Deliberately not calling initialize()
        
        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": "Hello!"}
        ]
        
        with pytest.raises(LIALInitError, match="LIAL adapter not initialized"):
            manager.send_messages(messages)

    def test_get_adapter_class_gemini(self):
        """Test _get_adapter_class for Gemini provider"""
        manager = LIALManager("gemini", {}, MagicMock())
        adapter_class = manager._get_adapter_class()
        assert adapter_class == GeminiAdapter

    def test_get_adapter_class_unsupported(self):
        """Test _get_adapter_class for unsupported provider"""
        manager = LIALManager("unsupported", {}, MagicMock())
        with pytest.raises(LIALInitError, match="Unsupported LLM provider: unsupported"):
            manager._get_adapter_class()