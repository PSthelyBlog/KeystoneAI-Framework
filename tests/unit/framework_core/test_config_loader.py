"""
Unit tests for the ConfigurationManager class.

This module tests all the functionality of the ConfigurationManager class
located in framework_core/config_loader.py.
"""

import os
import pytest
import tempfile
import yaml
from unittest.mock import patch, mock_open, MagicMock

from framework_core.config_loader import ConfigurationManager
from framework_core.exceptions import ConfigError

class TestConfigurationManager:
    """Test suite for the ConfigurationManager class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config_manager = ConfigurationManager()
        assert config_manager.config_path == os.path.join("config", "config.yaml")
        assert config_manager.cmd_args == {}
        assert config_manager.config == {}
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        config_path = "custom_config.yaml"
        cmd_args = {"llm_provider": "anthropic"}
        config_manager = ConfigurationManager(config_path=config_path, cmd_args=cmd_args)
        assert config_manager.config_path == config_path
        assert config_manager.cmd_args == cmd_args
        assert config_manager.config == {}
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="""
llm_provider: gemini
context_definition_file: ./FRAMEWORK_CONTEXT.md
llm_settings:
  gemini:
    model_name: gemini-1.0-pro
    temperature: 0.5
""")
    def test_load_configuration_with_valid_config_file(self, mock_file, mock_exists):
        """Test loading configuration from a valid file."""
        mock_exists.return_value = True
        
        config_manager = ConfigurationManager("config.yaml")
        result = config_manager.load_configuration()
        
        assert result is True
        assert config_manager.config["llm_provider"] == "gemini"
        assert config_manager.config["context_definition_file"] == "./FRAMEWORK_CONTEXT.md"
        assert config_manager.config["llm_settings"]["gemini"]["model_name"] == "gemini-1.0-pro"
        assert config_manager.config["llm_settings"]["gemini"]["temperature"] == 0.5
        
        # Default values should be preserved for keys not in the config file
        assert "teps_settings" in config_manager.config
        assert "logging" in config_manager.config
        assert "message_history" in config_manager.config
        assert "ui" in config_manager.config
    
    @patch('os.path.exists')
    def test_load_configuration_with_missing_config_file(self, mock_exists):
        """Test loading configuration when the config file is missing."""
        mock_exists.return_value = False
        
        config_manager = ConfigurationManager("missing_config.yaml")
        result = config_manager.load_configuration()
        
        assert result is True
        # Should use default configurations
        assert config_manager.config["llm_provider"] == "gemini"
        assert config_manager.config["context_definition_file"] == "./FRAMEWORK_CONTEXT.md"
        assert config_manager.config["llm_settings"]["gemini"]["model_name"] == "gemini-2.5-flash-preview-04-17"
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="""
llm_provider: gemini
context_definition_file: ./FRAMEWORK_CONTEXT.md
llm_settings:
  gemini:
    model_name: gemini-1.0-pro
    temperature: 0.5
""")
    def test_load_configuration_with_cmd_args_override(self, mock_file, mock_exists):
        """Test command-line arguments overriding file configuration."""
        mock_exists.return_value = True
        
        cmd_args = {
            "llm_provider": "anthropic",
            "llm_settings.anthropic.model_name": "claude-3-opus",
            "logging.level": "DEBUG"
        }
        
        config_manager = ConfigurationManager("config.yaml", cmd_args=cmd_args)
        result = config_manager.load_configuration()
        
        assert result is True
        # Command-line args should override file config
        assert config_manager.config["llm_provider"] == "anthropic"
        assert config_manager.config["llm_settings"]["anthropic"]["model_name"] == "claude-3-opus"
        assert config_manager.config["logging"]["level"] == "DEBUG"
        
        # Original file values should be preserved when not overridden
        assert config_manager.config["context_definition_file"] == "./FRAMEWORK_CONTEXT.md"
        assert config_manager.config["llm_settings"]["gemini"]["model_name"] == "gemini-1.0-pro"
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="invalid: yaml: -")
    def test_load_configuration_with_invalid_yaml(self, mock_file, mock_exists):
        """Test loading configuration with invalid YAML structure."""
        mock_exists.return_value = True
        
        # Mock yaml.safe_load to raise an exception
        with patch('yaml.safe_load', side_effect=yaml.YAMLError("Invalid YAML")):
            config_manager = ConfigurationManager("config.yaml")
            
            with pytest.raises(ConfigError) as excinfo:
                config_manager.load_configuration()
            
            assert "Failed to load configuration" in str(excinfo.value)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_load_configuration_with_empty_config_file(self, mock_file, mock_exists):
        """Test loading configuration with an empty config file."""
        mock_exists.return_value = True
        
        config_manager = ConfigurationManager("config.yaml")
        result = config_manager.load_configuration()
        
        assert result is True
        # Should use default configurations
        assert config_manager.config["llm_provider"] == "gemini"
        assert config_manager.config["context_definition_file"] == "./FRAMEWORK_CONTEXT.md"
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="""
# Missing required llm_provider
context_definition_file: ./FRAMEWORK_CONTEXT.md
""")
    def test_load_configuration_missing_required_keys(self, mock_file, mock_exists):
        """Test validation when required keys are missing in the config file."""
        mock_exists.return_value = True
        
        # Override default config to test validation
        with patch.object(ConfigurationManager, '_get_default_config', return_value={}):
            config_manager = ConfigurationManager("config.yaml")
            
            with pytest.raises(ConfigError) as excinfo:
                config_manager.load_configuration()
            
            assert "LLM provider" in str(excinfo.value)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="""
llm_provider: gemini
# Missing context_definition_file
""")
    def test_load_configuration_missing_context_file(self, mock_file, mock_exists):
        """Test validation when context_definition_file is missing."""
        mock_exists.return_value = True
        
        # Override default config to test validation
        with patch.object(ConfigurationManager, '_get_default_config', return_value={"llm_provider": "gemini"}):
            config_manager = ConfigurationManager("config.yaml")
            
            with pytest.raises(ConfigError) as excinfo:
                config_manager.load_configuration()
            
            assert "Context definition file" in str(excinfo.value)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="""
llm_provider: gemini
context_definition_file: ./FRAMEWORK_CONTEXT.md
# Missing llm_settings for gemini
""")
    def test_load_configuration_missing_provider_settings(self, mock_file, mock_exists):
        """Test loading configuration when provider settings are missing."""
        mock_exists.return_value = True
        
        config_manager = ConfigurationManager("config.yaml")
        result = config_manager.load_configuration()
        
        assert result is True
        # Should have llm_settings structure
        assert "llm_settings" in config_manager.config
        assert "gemini" in config_manager.config["llm_settings"]
        # The provider settings should contain the default values from _get_default_config
        assert "model_name" in config_manager.config["llm_settings"]["gemini"]
        assert "temperature" in config_manager.config["llm_settings"]["gemini"]
        assert "max_output_tokens" in config_manager.config["llm_settings"]["gemini"]
    
    def test_get_context_definition_path_absolute(self):
        """Test getting context definition path when it's an absolute path."""
        config_manager = ConfigurationManager()
        config_manager.config = {"context_definition_file": "/absolute/path/to/FRAMEWORK_CONTEXT.md"}
        
        path = config_manager.get_context_definition_path()
        assert path == "/absolute/path/to/FRAMEWORK_CONTEXT.md"
    
    @patch('os.path.dirname')
    @patch('os.path.abspath')
    def test_get_context_definition_path_relative(self, mock_abspath, mock_dirname):
        """Test getting context definition path when it's a relative path."""
        # Setup mocks
        mock_dirname.return_value = "/config/dir"
        mock_abspath.side_effect = lambda path: path  # Just return the path
        
        config_manager = ConfigurationManager("config/config.yaml")
        config_manager.config = {"context_definition_file": "./FRAMEWORK_CONTEXT.md"}
        
        # Mock the second abspath call for the joined path
        with patch('os.path.abspath', side_effect=["/config/dir/config/config.yaml", "/config/dir/./FRAMEWORK_CONTEXT.md"]):
            path = config_manager.get_context_definition_path()
            assert path == "/config/dir/./FRAMEWORK_CONTEXT.md"
    
    def test_get_context_definition_path_missing(self):
        """Test getting context definition path when it's missing."""
        config_manager = ConfigurationManager()
        config_manager.config = {}
        
        with pytest.raises(ConfigError) as excinfo:
            config_manager.get_context_definition_path()
        
        assert "Context definition file path not configured" in str(excinfo.value)
    
    def test_get_llm_provider(self):
        """Test getting the LLM provider."""
        config_manager = ConfigurationManager()
        config_manager.config = {"llm_provider": "gemini"}
        
        provider = config_manager.get_llm_provider()
        assert provider == "gemini"
    
    def test_get_llm_provider_missing(self):
        """Test getting the LLM provider when it's missing."""
        config_manager = ConfigurationManager()
        config_manager.config = {}
        
        with pytest.raises(ConfigError) as excinfo:
            config_manager.get_llm_provider()
        
        assert "LLM provider not configured" in str(excinfo.value)
    
    def test_get_llm_settings(self):
        """Test getting LLM settings for the configured provider."""
        config_manager = ConfigurationManager()
        config_manager.config = {
            "llm_provider": "gemini",
            "llm_settings": {
                "gemini": {
                    "model_name": "gemini-1.0-pro",
                    "temperature": 0.5
                }
            }
        }
        
        settings = config_manager.get_llm_settings()
        assert settings == {
            "model_name": "gemini-1.0-pro",
            "temperature": 0.5
        }
    
    def test_get_llm_settings_empty(self):
        """Test getting LLM settings when they are empty."""
        config_manager = ConfigurationManager()
        config_manager.config = {
            "llm_provider": "gemini",
            "llm_settings": {
                "gemini": {}
            }
        }
        
        settings = config_manager.get_llm_settings()
        assert settings == {}
    
    def test_get_llm_settings_missing(self):
        """Test getting LLM settings when they are missing."""
        config_manager = ConfigurationManager()
        config_manager.config = {
            "llm_provider": "gemini",
            "llm_settings": {}
        }
        
        with pytest.raises(ConfigError) as excinfo:
            config_manager.get_llm_settings()
        
        assert "Settings for LLM provider 'gemini' not found" in str(excinfo.value)
    
    def test_get_teps_settings(self):
        """Test getting TEPS settings."""
        config_manager = ConfigurationManager()
        config_manager.config = {
            "teps_settings": {
                "allowlist_file": ".project_teps_allowlist.json",
                "default_confirmation": False
            }
        }
        
        settings = config_manager.get_teps_settings()
        assert settings == {
            "allowlist_file": ".project_teps_allowlist.json",
            "default_confirmation": False
        }
    
    def test_get_teps_settings_missing(self):
        """Test getting TEPS settings when they are missing."""
        config_manager = ConfigurationManager()
        config_manager.config = {}
        
        settings = config_manager.get_teps_settings()
        assert settings == {}
    
    def test_get_logging_settings(self):
        """Test getting logging settings."""
        config_manager = ConfigurationManager()
        config_manager.config = {
            "logging": {
                "level": "DEBUG",
                "format": "custom_format",
                "file": "custom.log"
            }
        }
        
        settings = config_manager.get_logging_settings()
        assert settings == {
            "level": "DEBUG",
            "format": "custom_format",
            "file": "custom.log"
        }
    
    def test_get_logging_settings_missing(self):
        """Test getting logging settings when they are missing."""
        config_manager = ConfigurationManager()
        config_manager.config = {}
        
        settings = config_manager.get_logging_settings()
        assert settings == {}
    
    def test_get_message_history_settings(self):
        """Test getting message history settings."""
        config_manager = ConfigurationManager()
        config_manager.config = {
            "message_history": {
                "max_length": 200,
                "pruning_strategy": "custom"
            }
        }
        
        settings = config_manager.get_message_history_settings()
        assert settings == {
            "max_length": 200,
            "pruning_strategy": "custom"
        }
    
    def test_get_message_history_settings_missing(self):
        """Test getting message history settings when they are missing."""
        config_manager = ConfigurationManager()
        config_manager.config = {}
        
        settings = config_manager.get_message_history_settings()
        assert settings == {}
    
    def test_get_ui_settings(self):
        """Test getting UI settings."""
        config_manager = ConfigurationManager()
        config_manager.config = {
            "ui": {
                "input_prompt": "custom> ",
                "use_color": False
            }
        }
        
        settings = config_manager.get_ui_settings()
        assert settings == {
            "input_prompt": "custom> ",
            "use_color": False
        }
    
    def test_get_ui_settings_missing(self):
        """Test getting UI settings when they are missing."""
        config_manager = ConfigurationManager()
        config_manager.config = {}
        
        settings = config_manager.get_ui_settings()
        assert settings == {}
    
    def test_update_config_recursive(self):
        """Test recursive update of configuration."""
        config_manager = ConfigurationManager()
        target = {
            "level1": {
                "key1": "value1",
                "key2": "value2"
            },
            "simple_key": "simple_value"
        }
        source = {
            "level1": {
                "key2": "new_value2",
                "key3": "value3"
            },
            "simple_key": "new_simple_value",
            "new_key": "new_value"
        }
        
        config_manager._update_config_recursive(target, source)
        
        assert target["level1"]["key1"] == "value1"  # Unchanged
        assert target["level1"]["key2"] == "new_value2"  # Updated
        assert target["level1"]["key3"] == "value3"  # Added
        assert target["simple_key"] == "new_simple_value"  # Updated
        assert target["new_key"] == "new_value"  # Added
    
    def test_apply_cmd_args_top_level(self):
        """Test applying command-line arguments at the top level."""
        config_manager = ConfigurationManager()
        config_manager.config = {"key1": "value1"}
        config_manager.cmd_args = {"key1": "new_value1", "key2": "value2"}
        
        config_manager._apply_cmd_args()
        
        assert config_manager.config["key1"] == "new_value1"
        assert config_manager.config["key2"] == "value2"
    
    def test_apply_cmd_args_nested(self):
        """Test applying command-line arguments with nested keys."""
        config_manager = ConfigurationManager()
        config_manager.config = {
            "level1": {
                "key1": "value1"
            }
        }
        config_manager.cmd_args = {
            "level1.key1": "new_value1",
            "level1.key2": "value2",
            "level2.key1": "value3"
        }
        
        config_manager._apply_cmd_args()
        
        assert config_manager.config["level1"]["key1"] == "new_value1"
        assert config_manager.config["level1"]["key2"] == "value2"
        assert config_manager.config["level2"]["key1"] == "value3"