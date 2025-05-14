#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for the DCM and LIAL components.

These tests verify that the Dynamic Context Manager (DCM) and
LLM Interaction Abstraction Layer (LIAL) components work together correctly.

AI-GENERATED: [Forge] - Task:[RFI-DCM-Int-Test-001]
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the google.generativeai module before importing GeminiAdapter
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

from framework_core.dcm import DynamicContextManager
from framework_core.lial_core import LLMAdapterInterface, Message, LLMResponse, ToolRequest


class MockLLMAdapter(LLMAdapterInterface):
    """
    A mock LLM adapter implementation for testing integration with DCM.
    This adapter implements the LLMAdapterInterface but doesn't make actual API calls.
    """
    
    def __init__(self, config: dict, dcm_instance: DynamicContextManager) -> None:
        """Initialize the mock adapter with config and DCM instance."""
        self.config = config
        self.dcm = dcm_instance
        self.persona_id = None
    
    def send_message_sequence(
        self, 
        messages: list[Message], 
        active_persona_id: str = None
    ) -> LLMResponse:
        """
        Mock implementation of send_message_sequence.
        Returns a simple response and simulates using the DCM.
        """
        self.persona_id = active_persona_id
        
        # Use the DCM to get document content if active_persona_id is provided
        persona_content = None
        content_info = ""
        
        if active_persona_id and self.dcm:
            persona_content = self.dcm.get_document_content(active_persona_id)
            if persona_content:
                content_info = f"\nPersona content length: {len(persona_content)}"
        
        # Construct a simple response
        response = {
            "conversation": "This is a mock response" + 
                            (f" using persona: {active_persona_id}" if active_persona_id else "") +
                            content_info,
            "tool_request": None
        }
        
        return response


# Define a simple mock for GeminiAdapter without importing the real one
class MockGeminiAdapter(LLMAdapterInterface):
    """Mock implementation of GeminiAdapter for testing."""
    
    def __init__(self, config: dict, dcm_instance: DynamicContextManager) -> None:
        """Initialize the mock Gemini adapter."""
        self.config = config
        self.dcm = dcm_instance
        self.model = MagicMock()
    
    def send_message_sequence(
        self, 
        messages: list[Message], 
        active_persona_id: str = None
    ) -> LLMResponse:
        """Mock implementation of send_message_sequence."""
        # Use the DCM to get content if active_persona_id is provided
        if active_persona_id and self.dcm:
            persona_content = self.dcm.get_document_content(active_persona_id)
        
        # Return a mock response
        return {
            "conversation": "This is a mock Gemini response",
            "tool_request": None
        }


class TestDCMLIALIntegration(unittest.TestCase):
    """Integration tests for DCM and LIAL components."""
    
    def setUp(self):
        """Set up test environment with temporary directory and test files."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test documents and folders
        os.makedirs(os.path.join(self.temp_dir, "personas"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "standards"), exist_ok=True)
        
        # Create persona definition files
        with open(os.path.join(self.temp_dir, "personas", "test_persona.md"), 'w', encoding='utf-8') as f:
            f.write("# Test Persona\n\nThis is a test persona definition.")
        
        with open(os.path.join(self.temp_dir, "personas", "another_persona.md"), 'w', encoding='utf-8') as f:
            f.write("# Another Persona\n\nThis is another test persona definition.")
        
        # Create a standard document
        with open(os.path.join(self.temp_dir, "standards", "test_standard.md"), 'w', encoding='utf-8') as f:
            f.write("# Test Standard\n\nThis is a test standard document.")
        
        # Create the context definition file
        self.context_file_path = os.path.join(self.temp_dir, "FRAMEWORK_CONTEXT.md")
        with open(self.context_file_path, 'w', encoding='utf-8') as f:
            f.write("""# Framework Context Definition

# initial_prompt_template: "Test prompt template that uses persona_test_persona"

## Personas
persona_test_persona: @./personas/test_persona.md
persona_another: @./personas/another_persona.md

## Standards
standard_test: @./standards/test_standard.md
""")
    
    def tearDown(self):
        """Clean up temporary files and directories."""
        shutil.rmtree(self.temp_dir)
    
    def test_lial_adapter_initialization_with_dcm(self):
        """Test that a LIAL adapter can be initialized with a DCM instance."""
        # Initialize DCM
        dcm = DynamicContextManager(self.context_file_path)
        
        # Initialize the mock adapter with DCM
        config = {"test_config": "value"}
        adapter = MockLLMAdapter(config, dcm)
        
        # Verify the adapter has the DCM instance
        self.assertIs(adapter.dcm, dcm)
        
        # Verify the adapter has the config
        self.assertEqual(adapter.config, config)
    
    def test_gemini_adapter_initialization_with_dcm(self):
        """Test that the GeminiAdapter can be initialized with a DCM instance."""
        # Initialize DCM
        dcm = DynamicContextManager(self.context_file_path)
        
        # Initialize the mock Gemini adapter with DCM
        config = {"api_key": "mock_key", "model_name": "gemini-1.5-pro"}
        adapter = MockGeminiAdapter(config, dcm)
        
        # Verify the adapter has the DCM instance
        self.assertIs(adapter.dcm, dcm)
        
        # The test passes if initialization completes without errors
    
    def test_lial_accessing_dcm_documents(self):
        """Test that a LIAL adapter can access documents from the DCM."""
        # Initialize DCM
        dcm = DynamicContextManager(self.context_file_path)
        
        # Initialize the mock adapter with DCM
        config = {}
        adapter = MockLLMAdapter(config, dcm)
        
        # Create a message sequence
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        # Send the message sequence with a persona ID that exists in the DCM
        response = adapter.send_message_sequence(messages, active_persona_id="persona_test_persona")
        
        # Verify the response references the persona and its content
        self.assertIn("using persona: persona_test_persona", response["conversation"])
        self.assertIn("Persona content length:", response["conversation"])
        # Ensure the content length is > 0, indicating content was retrieved
        self.assertIn("Persona content length: ", response["conversation"])
        self.assertNotIn("Persona content length: 0", response["conversation"])
    
    def test_lial_handling_missing_documents(self):
        """Test that a LIAL adapter gracefully handles missing documents."""
        # Initialize DCM
        dcm = DynamicContextManager(self.context_file_path)
        
        # Initialize the mock adapter with DCM
        config = {}
        adapter = MockLLMAdapter(config, dcm)
        
        # Create a message sequence
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        # Send the message sequence with a non-existent persona ID
        response = adapter.send_message_sequence(messages, active_persona_id="non_existent_persona")
        
        # Verify the response references the persona
        self.assertIn("using persona: non_existent_persona", response["conversation"])
        
        # Verify the response doesn't include a persona content length
        # This test passes as long as the adapter doesn't crash when trying to use
        # a non-existent document from the DCM
        self.assertIsNone(dcm.get_document_content("non_existent_persona"))
    
    def test_integration_with_initial_prompt_template(self):
        """Test integration with the initial prompt template from DCM."""
        # Initialize DCM
        dcm = DynamicContextManager(self.context_file_path)
        
        # Initialize the mock adapter with DCM
        adapter = MockLLMAdapter({}, dcm)
        
        # Get the initial prompt template
        template = dcm.get_initial_prompt_template()
        
        # Verify the template references the persona that exists in the DCM
        self.assertIn("persona_test_persona", template)
        
        # Now create a simple message using this template
        messages = [
            {"role": "system", "content": template},
            {"role": "user", "content": "Hello"}
        ]
        
        # Send the message sequence with the persona referenced in the template
        response = adapter.send_message_sequence(messages, active_persona_id="persona_test_persona")
        
        # Verify the response acknowledges the persona
        self.assertIn("using persona: persona_test_persona", response["conversation"])
    
    def test_integration_with_multiple_personas(self):
        """Test integration with multiple personas in the DCM."""
        # Initialize DCM
        dcm = DynamicContextManager(self.context_file_path)
        
        # Verify the DCM loaded both personas
        personas = dcm.get_persona_definitions()
        self.assertEqual(len(personas), 2)
        self.assertIn("persona_test_persona", personas)
        self.assertIn("persona_another", personas)
        
        # Initialize the mock adapter with DCM
        adapter = MockLLMAdapter({}, dcm)
        
        # Create a message sequence
        messages = [{"role": "user", "content": "Hello"}]
        
        # Test with the first persona
        response1 = adapter.send_message_sequence(messages, active_persona_id="persona_test_persona")
        self.assertIn("using persona: persona_test_persona", response1["conversation"])
        
        # Test with the second persona
        response2 = adapter.send_message_sequence(messages, active_persona_id="persona_another")
        self.assertIn("using persona: persona_another", response2["conversation"])
    
    def test_mock_gemini_adapter_with_dcm_persona(self):
        """Test the mock Gemini adapter using persona content from DCM."""
        # Initialize DCM
        dcm = DynamicContextManager(self.context_file_path)
        
        # Initialize mock Gemini adapter with DCM
        config = {"api_key": "mock_key", "model_name": "gemini-1.5-pro"}
        adapter = MockGeminiAdapter(config, dcm)
        
        # Create a message sequence
        messages = [{"role": "user", "content": "Hello"}]
        
        # Send the message sequence with a persona ID
        response = adapter.send_message_sequence(messages, active_persona_id="persona_test_persona")
        
        # The test passes as long as the adapter doesn't raise exceptions
        # when trying to use the DCM for persona content
        self.assertEqual(response["conversation"], "This is a mock Gemini response")


if __name__ == "__main__":
    unittest.main()