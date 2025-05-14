"""
Error handler for the Framework Core Application.

This module provides centralized error handling functionality.
"""

import traceback
from typing import Optional, Dict, Any

from framework_core.utils.logging_utils import setup_logger

class ErrorHandler:
    """
    Centralized error handler for the Framework Core Application.
    Handles and standardizes error responses.
    """
    
    def __init__(self):
        """
        Initialize the Error Handler.
        """
        self.logger = setup_logger("error_handler")
        
    def handle_error(
        self, 
        error_type: str, 
        error_message: str, 
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Handle an error, log it, and return a standardized message.
        
        Args:
            error_type: The type of error
            error_message: The error message
            exception: Optional exception object
            context: Optional context information
            
        Returns:
            Formatted error message for user display
        """
        # Log the error with traceback if exception provided
        if exception:
            self.logger.error(
                f"{error_type}: {error_message}\n"
                f"Exception: {str(exception)}\n"
                f"{traceback.format_exc()}"
            )
        else:
            self.logger.error(f"{error_type}: {error_message}")
            
        # Log additional context if provided
        if context:
            self.logger.error(f"Error context: {context}")
            
        # Return standardized message
        return error_message
