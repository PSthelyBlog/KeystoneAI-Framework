"""
LLM Interaction Abstraction Layer (LIAL) manager for the Framework Core Application.

This module provides an interface for interacting with the LIAL component.
"""

from typing import Optional, Dict, Any, List

from framework_core.utils.logging_utils import setup_logger
from framework_core.exceptions import LIALInitError, ConfigError # Added ConfigError

class LIALManager:
    """
    Interface for interacting with the LLM Interaction Abstraction Layer (LIAL) component.
    """
    
    def __init__(
        self, 
        llm_provider: str, 
        llm_settings: Dict[str, Any],
        dcm_manager: 'DCMManager' 
    ):
        """
        Initialize the LIAL Manager.
        
        Args:
            llm_provider: Provider name (e.g., "gemini")
            llm_settings: LLM-specific settings
            dcm_manager: DCM manager instance for context retrieval
        """
        self.logger = setup_logger("lial_manager")
        self.llm_provider = llm_provider
        self.llm_settings = llm_settings
        self.dcm_manager = dcm_manager
        self.adapter_instance = None
        # self.lial_instance = None # Removed as LIAL class is not directly used, adapter is the instance
        # self.adapter = None # Renamed to adapter_instance for clarity
        
    def initialize(self) -> bool: # Return type changed to bool for consistency
        """
        Initialize the LIAL component with the appropriate adapter.
        
        Raises:
            LIALInitError: If initialization fails
        """
        if not self.llm_provider:
            # Use ConfigError for consistency with other manager initializations
            raise ConfigError("LLM provider is required for LIAL initialization")
            
        try:
            # Get adapter class based on provider
            adapter_class = self._get_adapter_class()
            
            # Extract provider-specific settings from the general llm_settings
            # Assuming llm_settings passed to LIALManager's __init__ is already the specific settings for the provider.
            # If llm_settings is a general dict like {"gemini": {...}, "anthropic": {...}}, then:
            # provider_specific_config = self.llm_settings.get(self.llm_provider, {})
            # For this fix, assuming self.llm_settings IS the specific config dict.
            
            # Initialize adapter
            self.logger.info(f"Initializing adapter for provider: {self.llm_provider}")
            # Ensure dcm_manager and its dcm_instance are valid before passing
            if not self.dcm_manager or not hasattr(self.dcm_manager, 'dcm_instance'):
                raise LIALInitError("DCMManager or its dcm_instance is not properly initialized before LIAL.")

            self.adapter_instance = adapter_class(
                config=self.llm_settings, # This should be the specific config for the adapter
                dcm_instance=self.dcm_manager.dcm_instance # Pass the actual DynamicContextManager instance
            )
            
            self.logger.info(f"LIAL initialized successfully with provider: {self.llm_provider}")
            return True # Added return True
            
        except Exception as e:
            self.logger.error(f"LIAL initialization failed: {str(e)}")
            raise LIALInitError(f"Failed to initialize LIAL: {str(e)}") from e
            
    def _get_adapter_class(self):
        """
        Get the appropriate adapter class based on the provider.
        
        Returns:
            Adapter class
            
        Raises:
            LIALInitError: If adapter not found for provider
        """
        # Corrected provider string to "gemini" to match config.yaml.example
        if self.llm_provider == "gemini": 
            from framework_core.adapters.gemini_adapter import GeminiAdapter
            return GeminiAdapter
        # Example for future provider
        # elif self.llm_provider == "anthropic":
        #     from framework_core.adapters.anthropic_adapter import AnthropicAdapter # Assuming it exists
        #     return AnthropicAdapter
        else:
            error_msg = f"Unsupported LLM provider: {self.llm_provider}"
            self.logger.error(error_msg)
            raise LIALInitError(error_msg) # Changed from ValueError to LIALInitError
            
    def send_messages(self, messages: List[Dict[str, Any]], active_persona_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send messages to the LLM and get a response.
        
        Args:
            messages: List of message dictionaries
            active_persona_id: Optional ID of the active persona.
            
        Returns:
            LLM response dictionary with conversation and optional tool request
            
        Raises:
            LIALInitError: If LIAL is not initialized
        """
        if not self.adapter_instance: # Changed from self.lial_instance
            error_msg = "LIAL adapter not initialized"
            self.logger.error(error_msg)
            raise LIALInitError(error_msg)
            
        self.logger.info(f"Sending {len(messages)} messages to LLM using persona: {active_persona_id or 'default'}")
        return self.adapter_instance.send_message_sequence(messages, active_persona_id=active_persona_id)