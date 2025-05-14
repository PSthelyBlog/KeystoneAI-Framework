#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic test for the DCM implementation using Python's built-in unittest framework.
"""

import os
import sys
import unittest
import tempfile
import shutil

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework_core.dcm import DynamicContextManager

class TestDCMBasic(unittest.TestCase):
    """Basic tests for the DynamicContextManager class."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test documents
        os.makedirs(os.path.join(self.temp_dir, "test_docs"), exist_ok=True)
        
        # Create the test documents
        with open(os.path.join(self.temp_dir, "test_docs", "test_doc_1.md"), 'w', encoding='utf-8') as f:
            f.write("# Test Document 1\n\nThis is test document 1.")
        
        with open(os.path.join(self.temp_dir, "test_docs", "test_doc_2.md"), 'w', encoding='utf-8') as f:
            f.write("# Test Document 2\n\nThis is test document 2.")
        
        with open(os.path.join(self.temp_dir, "test_docs", "test_persona.md"), 'w', encoding='utf-8') as f:
            f.write("# Test Persona\n\nThis is a test persona.")
        
        # Create the context file
        self.context_file_path = os.path.join(self.temp_dir, "test_context.md")
        with open(self.context_file_path, 'w', encoding='utf-8') as f:
            f.write("""# Test Framework Context

# initial_prompt_template: "This is a test prompt template"

## Test Section
test_doc_1: @./test_docs/test_doc_1.md
test_doc_2: @./test_docs/test_doc_2.md

## Personas
test_persona: @./test_docs/test_persona.md
""")
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_dcm_initialization(self):
        """Test basic DCM initialization and document loading."""
        dcm = DynamicContextManager(self.context_file_path)
        
        # Check document loading
        self.assertEqual(len(dcm._loaded_docs), 3)
        self.assertIn("test_doc_1", dcm._loaded_docs)
        self.assertIn("test_doc_2", dcm._loaded_docs)
        self.assertIn("test_persona", dcm._loaded_docs)
        
        # Check persona identification
        self.assertEqual(len(dcm._persona_definitions), 1)
        self.assertIn("test_persona", dcm._persona_definitions)
        
        # Check initial prompt template
        self.assertEqual(dcm._initial_prompt_template, "This is a test prompt template")
    
    def test_get_methods(self):
        """Test the get methods of DCM."""
        dcm = DynamicContextManager(self.context_file_path)
        
        # Test get_full_initial_context
        context = dcm.get_full_initial_context()
        self.assertEqual(len(context), 3)
        self.assertIn("test_doc_1", context)
        
        # Test get_document_content
        content = dcm.get_document_content("test_doc_1")
        self.assertIn("This is test document 1.", content)
        
        # Test get_persona_definitions
        personas = dcm.get_persona_definitions()
        self.assertEqual(len(personas), 1)
        self.assertIn("test_persona", personas)
        
        # Test get_initial_prompt_template
        template = dcm.get_initial_prompt_template()
        self.assertEqual(template, "This is a test prompt template")
    
    def test_missing_document(self):
        """Test handling of missing referenced documents."""
        # Create a context file with a missing document reference
        missing_context_path = os.path.join(self.temp_dir, "missing_context.md")
        with open(missing_context_path, 'w', encoding='utf-8') as f:
            f.write("""# Missing Document Test
## Documents
missing_doc: @./non_existent.md
valid_doc: @./test_docs/test_doc_1.md
""")
        
        # Initialize DCM
        dcm = DynamicContextManager(missing_context_path)
        
        # Check that the valid document was loaded
        self.assertIn("valid_doc", dcm._loaded_docs)
        
        # Check that the missing document was not loaded
        self.assertNotIn("missing_doc", dcm._loaded_docs)

if __name__ == "__main__":
    unittest.main()