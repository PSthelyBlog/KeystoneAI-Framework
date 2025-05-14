"""
Exceptions for the Framework Core Application.

This module defines all custom exceptions used throughout the framework.
"""

class ConfigError(Exception):
    """Error related to configuration loading or validation."""
    pass

class DCMInitError(Exception):
    """Error in initializing the Dynamic Context Manager."""
    pass

class LIALInitError(Exception):
    """Error in initializing the LLM Interaction Abstraction Layer."""
    pass

class TEPSInitError(Exception):
    """Error in initializing the Tool Execution & Permission Service."""
    pass

class ComponentInitError(Exception):
    """Error in initializing a generic component."""
    pass

class ToolExecutionError(Exception):
    """Error in executing a tool request."""
    
    def __init__(self, message: str, error_result: dict = None):
        """
        Initialize with message and optional error result.
        
        Args:
            message: Error message
            error_result: Optional dict with structured error info
        """
        super().__init__(message)
        self.error_result = error_result
