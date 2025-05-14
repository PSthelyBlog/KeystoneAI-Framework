"""
Tool Execution & Permission Service (TEPS) manager for the Framework Core Application.

This module provides an interface for interacting with the TEPS component.
"""

from typing import Optional, Dict, Any

from framework_core.utils.logging_utils import setup_logger
from framework_core.exceptions import TEPSInitError

# Corrected import
from framework_core.teps import TEPSEngine 

class TEPSManager:
    """
    Interface for interacting with the Tool Execution & Permission Service (TEPS) component.
    """
    
    def __init__(self, teps_settings: Optional[Dict[str, Any]] = None): # Added Optional and default
        """
        Initialize the TEPS Manager.
        
        Args:
            teps_settings: TEPS configuration settings
        """
        self.logger = setup_logger("teps_manager")
        self.teps_settings = teps_settings or {} # Ensure teps_settings is a dict
        self.teps_instance = None
        
    def initialize(self) -> None: # Changed return type to None for consistency
        """
        Initialize the TEPS component.
        
        Raises:
            TEPSInitError: If initialization fails
        """
        try:
            # from framework_core.teps import TEPSEngine # Import already at top level
            
            self.logger.info("Initializing TEPS")
            # Corrected instantiation
            self.teps_instance = TEPSEngine(config=self.teps_settings) 
            
            self.logger.info("TEPS initialized successfully")
            # return True # No need to return True if return type is None
            
        except Exception as e:
            self.logger.error(f"TEPS initialization failed: {str(e)}")
            raise TEPSInitError(f"Failed to initialize TEPS: {str(e)}") from e
            
    def execute_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool request via TEPS.
        
        Args:
            tool_request: The tool request to execute
            
        Returns:
            Tool execution result
            
        Raises:
            TEPSInitError: If TEPS is not initialized
        """
        if not self.teps_instance:
            error_msg = "TEPS not initialized"
            self.logger.error(error_msg)
            raise TEPSInitError(error_msg)
            
        tool_name = tool_request.get("tool_name", "unknown")
        self.logger.info(f"Executing tool: {tool_name} via TEPSManager") # Added context
        
        return self.teps_instance.execute_tool(tool_request)