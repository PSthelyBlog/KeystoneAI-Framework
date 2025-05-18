#!/usr/bin/env python3
"""
Enhanced main entry point for the KeystoneAI Framework with fixed configuration.
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

def main() -> int:
    """
    Main entry point function.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    logger = setup_logger("main")
    logger.info("Starting Framework Core Application")
    
    try:
        # Use absolute path to config file
        current_dir = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(current_dir, "config", "config.yaml")
        
        # Print configuration info
        print(f"Using configuration file: {config_path}")
        
        # Check if the config file exists
        if not os.path.exists(config_path):
            print(f"ERROR: Configuration file not found: {config_path}")
            return 1
            
        # Initialize configuration
        config_manager = ConfigurationManager(config_path)
        if not config_manager.load_configuration():
            logger.error("Failed to load configuration")
            return 1
            
        # Initialize framework controller
        controller = FrameworkController(config_manager)
        if not controller.initialize():
            logger.error("Failed to initialize framework controller")
            return 1
            
        # Check persona definitions
        persona_defs = controller.dcm_manager.get_persona_definitions()
        print(f"Available personas: {', '.join([pid.replace('persona_', '') for pid in persona_defs.keys()])}")
        
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