#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple validation script for the DCM implementation.
"""

import os
import sys
import logging

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from framework_core.dcm import DynamicContextManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dcm_validation")

def validate_dcm():
    """Run a simple validation of the DCM implementation."""
    logger.info("Starting DCM validation...")
    
    # Path to the test context file
    test_context_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_framework_context.md'))
    
    try:
        # Create a DCM instance
        dcm = DynamicContextManager(test_context_file)
        
        # Check if the prompt template was loaded
        prompt_template = dcm.get_initial_prompt_template()
        logger.info(f"Prompt template: {prompt_template}")
        assert prompt_template == "This is a test prompt template", "Prompt template not loaded correctly"
        
        # Check if documents were loaded
        documents = dcm.get_full_initial_context()
        logger.info(f"Loaded documents: {list(documents.keys())}")
        assert len(documents) == 3, f"Expected 3 documents, got {len(documents)}"
        
        # Check document content
        test_doc_1 = dcm.get_document_content("test_doc_1")
        logger.info(f"test_doc_1 content: {test_doc_1}")
        assert "This is the content of test document 1." in test_doc_1, "test_doc_1 content not loaded correctly"
        
        # Check persona definitions
        personas = dcm.get_persona_definitions()
        logger.info(f"Loaded personas: {list(personas.keys())}")
        assert len(personas) == 1, f"Expected 1 persona, got {len(personas)}"
        assert "test_persona" in personas, "test_persona not found in persona definitions"
        
        logger.info("All validation checks passed! DCM is working correctly.")
        return True
    
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = validate_dcm()
    sys.exit(0 if success else 1)