#!/usr/bin/env python3
"""
Comprehensive diagnostic tool for the KeystoneAI Framework.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from framework_core.config_loader import ConfigurationManager
from framework_core.controller import FrameworkController

def setup_logging():
    """Set up logging for the diagnostic tool."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("diagnose")

def diagnose_framework():
    """Run diagnostics on the framework."""
    logger = setup_logging()
    
    logger.info("KeystoneAI Framework Diagnostics")
    logger.info("-" * 50)
    
    # Check for config files
    config_path = os.path.abspath("config/config.yaml")
    context_path = os.path.abspath("config/FRAMEWORK_CONTEXT.md")
    
    logger.info(f"Checking configuration files:")
    logger.info(f"  Config file: {config_path} - {'Exists' if os.path.exists(config_path) else 'MISSING'}")
    logger.info(f"  Context file: {context_path} - {'Exists' if os.path.exists(context_path) else 'MISSING'}")
    
    if not os.path.exists(config_path) or not os.path.exists(context_path):
        logger.error("Configuration files are missing!")
        return 1
    
    # Check environment variables
    logger.info("\nChecking environment variables:")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        logger.error("  GEMINI_API_KEY is not set!")
    else:
        masked_key = gemini_key[:4] + "..." + gemini_key[-4:] if len(gemini_key) > 8 else "****"
        logger.info(f"  GEMINI_API_KEY is set: {masked_key}")
    
    # Initialize the framework components
    logger.info("\nInitializing framework components:")
    try:
        logger.info("  Loading configuration...")
        config_manager = ConfigurationManager(config_path)
        if not config_manager.load_configuration():
            logger.error("  Failed to load configuration!")
            return 1
        
        logger.info("  Framework settings:")
        framework_settings = config_manager.get_framework_settings()
        for key, value in framework_settings.items():
            logger.info(f"    {key}: {value}")
        
        logger.info("  Initializing controller...")
        controller = FrameworkController(config_manager)
        if not controller.initialize():
            logger.error("  Failed to initialize controller!")
            return 1
        
        # Check persona definitions
        logger.info("\nChecking persona definitions:")
        persona_defs = controller.dcm_manager.get_persona_definitions()
        if not persona_defs:
            logger.error("  No persona definitions found!")
        else:
            logger.info(f"  Found {len(persona_defs)} persona(s):")
            for pid in persona_defs:
                logger.info(f"    - {pid}")
            
            # Check /persona command compatibility
            valid_persona_ids = [pid.replace("persona_", "") for pid in persona_defs.keys()]
            logger.info(f"\n  Valid IDs for /persona command: {', '.join(valid_persona_ids)}")
            
            # Check if personas are correctly parsed
            for key in persona_defs.keys():
                if not key.startswith("persona_"):
                    logger.warning(f"  Warning: Persona key {key} does not start with 'persona_' prefix!")
        
        # Check initial prompt
        logger.info("\nChecking initial prompt:")
        initial_prompt = controller.dcm_manager.get_initial_prompt()
        if not initial_prompt:
            logger.warning("  No initial prompt found!")
        else:
            logger.info(f"  Initial prompt: {initial_prompt[:50]}...")
        
        logger.info("\nDiagnostics completed successfully.")
        return 0
        
    except Exception as e:
        logger.error(f"Error during diagnostics: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(diagnose_framework())