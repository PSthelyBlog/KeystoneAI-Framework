"""
Dynamic Context Manager (DCM) manager for the Framework Core Application.

This module provides an interface for interacting with the DCM component.
"""

from typing import Optional, Dict, Any, List

from framework_core.utils.logging_utils import setup_logger
from framework_core.exceptions import DCMInitError, ConfigError # Added ConfigError

class DCMManager:
    """
    Interface for interacting with the Dynamic Context Manager (DCM) component.
    """
    
    def __init__(self, context_definition_path: Optional[str] = None): # Added Optional and default
        """
        Initialize the DCM Manager.
        
        Args:
            context_definition_path: Path to the context definition file
        """
        self.logger = setup_logger("dcm_manager")
        self.context_definition_path = context_definition_path
        self.dcm_instance = None
        
    def initialize(self) -> None: # Changed return type
        """
        Initialize the DCM component.
        
        Raises:
            DCMInitError: If initialization fails
            ConfigError: If required configuration is missing
        """
        if not self.context_definition_path:
            raise ConfigError("Context definition path is required for DCM initialization")
            
        # No need to check for os.path.exists here, DCM itself will handle it and raise FileNotFoundError
        
        try:
            from framework_core.dcm import DynamicContextManager
            self.dcm_instance = DynamicContextManager(self.context_definition_path, logger=self.logger) # Pass logger
            self.logger.info(f"DCM initialized with context definition: {self.context_definition_path}")
            # return True # No longer returning bool
        except Exception as e:
            self.logger.error(f"DCM initialization failed: {str(e)}", exc_info=True) # Added exc_info
            raise DCMInitError(f"Failed to initialize DCM: {str(e)}") from e
            
    def get_initial_prompt(self) -> Optional[str]: # Renamed from get_initial_prompt_template for controller
        """
        Get the initial prompt template from DCM.
        
        Returns:
            The initial prompt template as a string, or None.
            
        Raises:
            DCMInitError: If DCM is not initialized
        """
        self._ensure_initialized()
        
        prompt = self.dcm_instance.get_initial_prompt_template() # This is the correct method in DCM
        if not prompt:
            self.logger.warning("No initial prompt template found in context definition")
            # Return a more generic default or None to let controller handle it
            return None 
            
        return prompt
        
    def get_full_context(self) -> Dict[str, Any]: # Changed to Any for flexibility
        """
        Get the full context loaded by DCM.
        
        Returns:
            Dictionary of all loaded documents
            
        Raises:
            DCMInitError: If DCM is not initialized
        """
        self._ensure_initialized()
        return self.dcm_instance.get_full_initial_context()
        
    def get_document_content(self, doc_id: str) -> Optional[str]:
        """
        Get the content of a specific document from DCM.
        
        Args:
            doc_id: The identifier of the document
            
        Returns:
            Document content as string, or None if not found
            
        Raises:
            DCMInitError: If DCM is not initialized
        """
        self._ensure_initialized()
        return self.dcm_instance.get_document_content(doc_id)
        
    def get_persona_definitions(self) -> Dict[str, str]:
        """
        Get all persona definitions from DCM.
        
        Returns:
            Dictionary mapping persona_id to definition content
            
        Raises:
            DCMInitError: If DCM is not initialized
        """
        self._ensure_initialized()
        return self.dcm_instance.get_persona_definitions()

    def get_document_ids(self) -> List[str]: # Added method from previous iteration for completeness
        """
        Get a list of all available document IDs.
        
        Returns:
            List of document IDs
        """
        self._ensure_initialized()
        # Assuming DynamicContextManager has a way to get all doc_ids, e.g., from _loaded_docs.keys()
        if hasattr(self.dcm_instance, '_loaded_docs'):
            return list(self.dcm_instance._loaded_docs.keys())
        self.logger.warning("DCM instance does not have _loaded_docs attribute to get document IDs.")
        return []
            
    def _ensure_initialized(self) -> None:
        """
        Ensure the DCM component is initialized.
        
        Raises:
            DCMInitError: If DCM is not initialized
        """
        if not self.dcm_instance:
            raise DCMInitError("DCM is not initialized")