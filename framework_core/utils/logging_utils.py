"""
Logging utilities for the Framework Core Application.

This module provides functions for setting up and configuring loggers.
"""

import logging
import os
from typing import Optional

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure a logger with the given name.
    
    Args:
        name: The name of the logger
        level: Optional logging level (if None, uses INFO or level from config)
        
    Returns:
        Configured logger
    """
    # Default to INFO if no level specified
    if level is None:
        level = "INFO"
        
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Don't add handler if logger already has handlers
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(numeric_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger
