"""
Configuration loader for the Framework Core Application.

This module handles loading, validating, and accessing configuration settings.
"""

import os
import yaml # Ensure PyYAML is installed
from typing import Optional, Dict, Any

from framework_core.utils.logging_utils import setup_logger
from framework_core.exceptions import ConfigError

class ConfigurationManager:
    """
    Manages loading, validation, and access to configuration settings.
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        cmd_args: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Configuration Manager.
        
        Args:
            config_path: Optional path to configuration file
            cmd_args: Optional command-line arguments
        """
        self.logger = setup_logger("config_manager")
        self.config_path = config_path or os.path.join("config", "config.yaml")
        self.cmd_args = cmd_args or {}
        self.config = {}
        
    def load_configuration(self) -> bool:
        """
        Load and validate configuration from file and command-line arguments.
        
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            # Set default configuration
            self.config = self._get_default_config()
            
            # Load configuration from file if it exists
            if os.path.exists(self.config_path):
                self.logger.info(f"Loading configuration from: {self.config_path}")
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                
                # Update config with file values
                self._update_config_recursive(self.config, file_config)
            else:
                self.logger.warning(f"Configuration file not found: {self.config_path}")
                self.logger.info("Using default configuration")
            
            # Override with command-line arguments
            if self.cmd_args:
                self.logger.info("Applying command-line argument overrides")
                self._apply_cmd_args()
            
            # Validate the final configuration
            self._validate_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise ConfigError(f"Failed to load configuration: {str(e)}") from e # Re-raise as ConfigError
            
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "llm_provider": "gemini", # CHANGED from gemini_2_5_pro
            "api_key_env_var": "GEMINI_API_KEY",
            "context_definition_file": "./FRAMEWORK_CONTEXT.md",
            
            "llm_settings": {
                "gemini": { # CHANGED from gemini_2_5_pro
                    "model_name": "gemini-2.5-flash-preview-04-17",
                    "temperature": 0.7,
                    "max_output_tokens": 8192,
                    "top_k": 40,
                    "top_p": 0.95
                }
                # Anthropic and Azure OpenAI settings would go here if used
            },
            
            "teps_settings": {
                "allowlist_file": ".project_teps_allowlist.json",
                "default_confirmation": False,
                "remember_confirmations": True
            },
            
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "framework.log"
            },
            
            "message_history": {
                "max_length": 100,
                "prioritize_system_messages": True,
                "pruning_strategy": "remove_oldest"
            },
            
            "ui": {
                "input_prompt": "> ",
                "assistant_prefix": "(AI): ",
                "system_prefix": "[System]: ",
                "error_prefix": "[Error]: ",
                "use_color": True
            }
        }
        
    def _update_config_recursive(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a target dictionary with values from a source dictionary.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._update_config_recursive(target[key], value)
            else:
                target[key] = value
                
    def _apply_cmd_args(self) -> None:
        """
        Apply command-line argument overrides to the configuration.
        """
        for key, value in self.cmd_args.items():
            # Split nested keys (e.g., "logging.level")
            if '.' in key:
                parts = key.split('.')
                target = self.config
                
                # Navigate to the nested dictionary
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                    
                # Set the value
                target[parts[-1]] = value
            else:
                # Set top-level key
                self.config[key] = value
                
    def _validate_config(self) -> None:
        """
        Validate the configuration.
        
        Raises:
            ConfigError: If validation fails
        """
        # Validate LLM provider
        llm_provider = self.config.get("llm_provider")
        if not llm_provider:
            raise ConfigError("LLM provider ('llm_provider') is required in configuration.")
            
        # Check if 'llm_settings' exists and if the specific provider is a key within it
        if "llm_settings" not in self.config or llm_provider not in self.config["llm_settings"]:
            # It's possible that llm_settings for the provider are all defaults or not needed by adapter
            self.logger.warning(f"Settings for LLM provider '{llm_provider}' not explicitly found in 'llm_settings'. Adapter will use defaults if any.")
            # Ensure the structure exists to avoid KeyErrors later
            if "llm_settings" not in self.config:
                self.config["llm_settings"] = {}
            if llm_provider not in self.config["llm_settings"]:
               self.config["llm_settings"][llm_provider] = {}

        # Validate context definition file
        context_file = self.config.get("context_definition_file")
        if not context_file:
            raise ConfigError("Context definition file ('context_definition_file') is required in configuration.")
            
    def get_context_definition_path(self) -> str:
        """
        Get the path to the context definition file.
        
        Returns:
            Context definition file path
        """
        path_str = self.config.get("context_definition_file")
        if not path_str: # Should be caught by _validate_config, but good to be safe
             raise ConfigError("Context definition file path not configured.")
        if os.path.isabs(path_str):
            return path_str
        # Resolve relative to the config file's directory
        config_dir = os.path.dirname(os.path.abspath(self.config_path))
        return os.path.abspath(os.path.join(config_dir, path_str))

    def get_llm_provider(self) -> str:
        """
        Get the current LLM provider.
        
        Returns:
            LLM provider name
        """
        provider = self.config.get("llm_provider")
        if not provider: # Should be caught by _validate_config
            raise ConfigError("LLM provider not configured.")
        return provider
        
    def get_llm_settings(self) -> Dict[str, Any]:
        """
        Get the LLM settings for the currently configured provider.
        
        Returns:
            LLM settings dictionary for the active provider.
        """
        provider = self.get_llm_provider()
        settings = self.config.get("llm_settings", {}).get(provider)
        # An empty dict {} is valid, means use adapter defaults.
        if settings is None:
            raise ConfigError(f"Settings for LLM provider '{provider}' not found.")
        return settings
        
    def get_teps_settings(self) -> Dict[str, Any]:
        """
        Get the TEPS settings.
        
        Returns:
            TEPS settings dictionary
        """
        return self.config.get("teps_settings", {})
        
    def get_logging_settings(self) -> Dict[str, Any]:
        """
        Get the logging settings.
        
        Returns:
            Logging settings dictionary
        """
        return self.config.get("logging", {})
        
    def get_message_history_settings(self) -> Dict[str, Any]:
        """
        Get the message history settings.
        
        Returns:
            Message history settings dictionary
        """
        return self.config.get("message_history", {})
        
    def get_ui_settings(self) -> Dict[str, Any]:
        """
        Get the UI settings.
        
        Returns:
            UI settings dictionary
        """
        return self.config.get("ui", {})