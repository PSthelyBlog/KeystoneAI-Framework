"""
Logging utilities for the Framework Core Application.

This module provides functions for setting up and configuring loggers.
"""

import logging
import os
from typing import Optional, Union

def setup_logger(
    name: str, 
    level: Optional[Union[str, int]] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure a logger with the given name.
    
    Args:
        name: The name of the logger
        level: Optional logging level (if None, uses INFO)
               Can be a string (e.g., "INFO") or an integer (e.g., logging.INFO)
        log_file: Optional path to a log file. If provided, a FileHandler will be added
        log_format: Optional custom log format string. If None, uses default format
        
    Returns:
        Configured logger
    """
    # Default to INFO if no level specified
    if level is None:
        level = "INFO"
        
    # Convert string level to logging constant if needed
    if isinstance(level, str):
        numeric_level = getattr(logging, level.upper(), logging.INFO)
    else:
        numeric_level = level
    
    # Default log format
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Clear existing handlers to prevent duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        # Ensure the directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    
    return logger