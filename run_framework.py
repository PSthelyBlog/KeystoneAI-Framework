#!/usr/bin/env python3
"""
Main entry point for the Framework Core Application.

This script initializes the framework components and starts the application.
"""

import os
import sys
import argparse
from typing import Dict, Any

# Add parent directory to path if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from framework_core.config_loader import ConfigurationManager
from framework_core.controller import FrameworkController
from framework_core.utils.logging_utils import setup_logger
from framework_core.exceptions import ConfigError, ComponentInitError

def parse_arguments() -> tuple:
    """
    Parse command-line arguments.
    
    Returns:
        Tuple of (config_path, args_dict)
    """
    parser = argparse.ArgumentParser(description="Framework Core Application")
    
    parser.add_argument(
        "--config", 
        "-c", 
        dest="config_path",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--log-level", 
        "-l", 
        dest="logging.level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    parser.add_argument(
        "--llm-provider", 
        dest="llm_provider",
        help="LLM provider to use"
    )
    
    parser.add_argument(
        "--context-file", 
        dest="context_definition_file",
        help="Path to context definition file"
    )
    
    # Parse args and convert to dict
    args = parser.parse_args()
    config_path = args.config_path
    
    # Remove config_path and convert the rest to a dict
    args_dict = {k: v for k, v in vars(args).items() if k != "config_path" and v is not None}
    
    return config_path, args_dict

def main() -> int:
    """
    Main entry point function.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    logger = setup_logger("main")
    logger.info("Starting Framework Core Application")
    
    try:
        # Parse command-line arguments
        config_path, cmd_args = parse_arguments()
        
        # Initialize configuration
        config_manager = ConfigurationManager(config_path, cmd_args)
        if not config_manager.load_configuration():
            logger.error("Failed to load configuration")
            return 1
            
        # Initialize framework controller
        controller = FrameworkController(config_manager)
        if not controller.initialize():
            logger.error("Failed to initialize framework controller")
            return 1
            
        # Run the application
        controller.run()
        
        return 0
        
    except ConfigError as e:
        logger.error(f"Configuration error: {str(e)}")
        print(f"Configuration error: {str(e)}")
        return 1
        
    except ComponentInitError as e:
        logger.error(f"Component initialization error: {str(e)}")
        print(f"Component initialization error: {str(e)}")
        return 1
        
    except KeyboardInterrupt:
        logger.info("Framework terminated by user")
        print("\nFramework terminated by user")
        return 0
        
    except Exception as e:
        logger.exception(f"Unhandled exception: {str(e)}")
        print(f"Unhandled exception: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())