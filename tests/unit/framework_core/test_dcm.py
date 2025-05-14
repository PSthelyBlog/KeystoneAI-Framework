#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final unit tests for the DCM implementation using Python's built-in unittest framework.

AI-GENERATED: [Forge] - Task:[RFI-DCM-Test-001]
"""

import os
import sys
import unittest
import tempfile
import shutil
import logging
from unittest.mock import MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework_core.dcm import DynamicContextManager

class TestDCMFinal(unittest.TestCase):
    """Final tests for the DynamicContextManager class."""
    
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
    
    def test_get_document_content_nonexistent(self):
        """Test get_document_content with non-existent document ID."""
        dcm = DynamicContextManager(self.context_file_path)
        
        # Test getting non-existent document
        content = dcm.get_document_content("non_existent")
        self.assertIsNone(content)
    
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
    
    def test_path_resolution(self):
        """Test path resolution for both relative and absolute paths."""
        # Create a context file with both relative and absolute paths
        path_context_file = os.path.join(self.temp_dir, "path_context.md")
        
        # Create an absolute path document
        abs_doc_path = os.path.join(self.temp_dir, "absolute_doc.md")
        with open(abs_doc_path, 'w', encoding='utf-8') as f:
            f.write("Absolute document content")
        
        with open(path_context_file, 'w', encoding='utf-8') as f:
            f.write(f"""# Path Resolution Test
## Documents
rel_doc: @./test_docs/test_doc_1.md
abs_doc: @{abs_doc_path}
""")
        
        # Initialize DCM
        dcm = DynamicContextManager(path_context_file)
        
        # Check that both documents were loaded
        self.assertIn("rel_doc", dcm._loaded_docs)
        self.assertIn("abs_doc", dcm._loaded_docs)
        self.assertIn("This is test document 1.", dcm._loaded_docs["rel_doc"])
        self.assertIn("Absolute document content", dcm._loaded_docs["abs_doc"])
    
    def test_different_prompt_template_formats(self):
        """Test different formats of initial prompt template."""
        # 1. With double quotes
        quotes_context_file = os.path.join(self.temp_dir, "quotes_context.md")
        with open(quotes_context_file, 'w', encoding='utf-8') as f:
            f.write('# initial_prompt_template: "Template with quotes"')
        
        dcm1 = DynamicContextManager(quotes_context_file)
        self.assertEqual(dcm1._initial_prompt_template, "Template with quotes")
        
        # 2. Without quotes
        no_quotes_context_file = os.path.join(self.temp_dir, "no_quotes_context.md")
        with open(no_quotes_context_file, 'w', encoding='utf-8') as f:
            f.write('# initial_prompt_template: Template without quotes')
        
        dcm2 = DynamicContextManager(no_quotes_context_file)
        self.assertEqual(dcm2._initial_prompt_template, "Template without quotes")
        
        # 3. With single quotes
        single_quotes_context_file = os.path.join(self.temp_dir, "single_quotes_context.md")
        with open(single_quotes_context_file, 'w', encoding='utf-8') as f:
            f.write("# initial_prompt_template: 'Template with single quotes'")
        
        dcm3 = DynamicContextManager(single_quotes_context_file)
        self.assertEqual(dcm3._initial_prompt_template, "Template with single quotes")
    
    def test_malformed_context_file(self):
        """Test that DCM handles malformed context file gracefully."""
        malformed_context_file = os.path.join(self.temp_dir, "malformed_context.md")
        with open(malformed_context_file, 'w', encoding='utf-8') as f:
            f.write("""# Malformed Context Test
## Documents
malformed_line_no_colon @./test_docs/test_doc_1.md
valid_doc: @./test_docs/test_doc_1.md
""")
        
        # Initialize DCM
        dcm = DynamicContextManager(malformed_context_file)
        
        # Check that the valid document was loaded
        self.assertIn("valid_doc", dcm._loaded_docs)
        
        # Check that the malformed line was ignored
        self.assertEqual(len(dcm._loaded_docs), 1)
    
    def test_custom_logger(self):
        """Test that DCM uses a custom logger if provided."""
        # Create a mock logger
        mock_logger = MagicMock()
        
        # Initialize DCM with the mock logger
        dcm = DynamicContextManager(self.context_file_path, logger=mock_logger)
        
        # Check that the logger was used
        self.assertIs(dcm.logger, mock_logger)
        
        # Check that at least some logging methods were called
        mock_logger.info.assert_called()
    
    def test_empty_context_file(self):
        """Test that DCM handles empty context file gracefully."""
        empty_context_file = os.path.join(self.temp_dir, "empty_context.md")
        with open(empty_context_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        # Initialize DCM
        dcm = DynamicContextManager(empty_context_file)
        
        # Check that no documents were loaded
        self.assertEqual(len(dcm._loaded_docs), 0)
        self.assertEqual(len(dcm._persona_definitions), 0)
        self.assertIsNone(dcm._initial_prompt_template)
    
    def test_sections_no_documents(self):
        """Test context file with sections but no documents."""
        sections_only_file = os.path.join(self.temp_dir, "sections_only.md")
        with open(sections_only_file, 'w', encoding='utf-8') as f:
            f.write("""# Sections Only
## Section 1
## Personas
## Documents
""")
        
        # Initialize DCM
        dcm = DynamicContextManager(sections_only_file)
        
        # Check that no documents were loaded
        self.assertEqual(len(dcm._loaded_docs), 0)
        self.assertEqual(len(dcm._persona_definitions), 0)
    
    def test_custom_encoding(self):
        """Test that DCM uses the specified encoding."""
        # Create a test file with specific encoding
        encoding_context_file = os.path.join(self.temp_dir, "encoding_context.md")
        with open(encoding_context_file, 'w', encoding='utf-8') as f:
            f.write("""# Encoding Test
## Documents
test_doc: @./test_docs/test_doc_1.md
""")
        
        # Initialize DCM with a custom encoding
        custom_encoding = "utf-8"  # Using UTF-8 since we're writing the file with UTF-8
        dcm = DynamicContextManager(encoding_context_file, encoding=custom_encoding)
        
        # Check that the document was loaded
        self.assertIn("test_doc", dcm._loaded_docs)

if __name__ == "__main__":
    unittest.main(verbosity=2)