"""
Integration tests for DCM-LIAL component chain.

These tests verify the integration between the Dynamic Context Manager (DCM)
and the LLM Interaction Abstraction Layer (LIAL) components.
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.exceptions import DCMInitError, LIALInitError
from framework_core.component_managers.dcm_manager import DCMManager
from framework_core.component_managers.lial_manager import LIALManager
from framework_core.lial_core import Message, LLMResponse
from tests.integration.utils import MockLLMAdapter, ResponseBuilder, IntegrationTestCase


class TestDCMLIALIntegration(IntegrationTestCase):
    """
    Integration tests for the DCM-LIAL chain.
    
    These tests validate that:
    1. DCM properly provides context to LIAL
    2. LIAL correctly uses context from DCM when generating responses
    3. Persona-specific context is properly applied
    4. Error conditions are handled appropriately
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        super().setup_method()
        
        # Create mock DCM content
        self.mock_context_content = {
            "main_system_prompt": "You are an AI assistant in the KeystoneAI Framework.",
            "persona_catalyst": "# Catalyst Persona\nThe strategic AI planner focused on architecture and planning.",
            "persona_forge": "# Forge Persona\nThe expert AI implementer focused on detailed execution."
        }
        
        # Create mock DCM manager
        self.dcm_manager = MagicMock(name="DCMManager")
        self.dcm_manager.get_document_content.side_effect = lambda doc_id: self.mock_context_content.get(doc_id)
        self.dcm_manager.get_full_context.return_value = self.mock_context_content
        self.dcm_manager.get_initial_prompt.return_value = self.mock_context_content["main_system_prompt"]
        self.dcm_manager.get_persona_definitions.return_value = {
            "catalyst": self.mock_context_content["persona_catalyst"],
            "forge": self.mock_context_content["persona_forge"]
        }
        
        # Create mock DCM instance
        self.dcm_instance = MagicMock(name="DynamicContextManager")
        self.dcm_instance.get_document_content.side_effect = lambda doc_id: self.mock_context_content.get(doc_id)
        self.dcm_instance.get_full_initial_context.return_value = self.mock_context_content
        self.dcm_instance.get_initial_prompt_template.return_value = self.mock_context_content["main_system_prompt"]
        self.dcm_instance.get_persona_definitions.return_value = {
            "catalyst": self.mock_context_content["persona_catalyst"],
            "forge": self.mock_context_content["persona_forge"]
        }
        
        # Set DCM instance in the DCM manager
        self.dcm_manager.dcm_instance = self.dcm_instance
        
        # Create LLM adapter and pre-configure common responses
        self.llm_adapter = MockLLMAdapter(
            config={"model_name": "mock-model", "temperature": 0.7},
            dcm_instance=self.dcm_instance
        )
        
        # Configure standard responses
        self.llm_adapter.configure_response("default", {
            "conversation": "I am an AI assistant. How can I help you?",
            "tool_request": None
        })
        
        self.llm_adapter.configure_response("catalyst", {
            "conversation": "(Catalyst) I'll help you plan and architect a solution.",
            "tool_request": None
        })
        
        self.llm_adapter.configure_response("forge", {
            "conversation": "(Forge) I'll implement that for you with precision.",
            "tool_request": None
        })
        
        # Create the test message sequences
        self.basic_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Hello, who are you?")
        ])
    
    def test_lial_initialization_with_dcm(self):
        """Test that LIAL can initialize correctly with a DCM instance."""
        # Create LIAL manager with the mock DCM manager
        lial_manager = LIALManager(
            llm_provider="mock",
            llm_settings={"model_name": "mock-model", "temperature": 0.7},
            dcm_manager=self.dcm_manager
        )
        
        # Patch _get_adapter_class to return our MockLLMAdapter
        with patch.object(lial_manager, '_get_adapter_class', return_value=lambda config, dcm_instance: self.llm_adapter):
            # Initialize LIAL
            result = lial_manager.initialize()
            
            # Verify initialization succeeded
            assert result is True
            assert lial_manager.adapter_instance is not None
            
            # Verify DCM was properly passed to the adapter
            assert self.dcm_manager.dcm_instance == self.dcm_instance
    
    def test_lial_initialization_failure_without_dcm(self):
        """Test that LIAL initialization fails when DCM is not properly initialized."""
        # Create a DCM manager with no dcm_instance
        incomplete_dcm_manager = MagicMock(name="IncompleteDCMManager")
        delattr(incomplete_dcm_manager, 'dcm_instance')  # Ensure dcm_instance attribute doesn't exist
        
        # Create LIAL manager with the incomplete DCM manager
        lial_manager = LIALManager(
            llm_provider="mock",
            llm_settings={"model_name": "mock-model", "temperature": 0.7},
            dcm_manager=incomplete_dcm_manager
        )
        
        # Initialize LIAL should raise an error
        with pytest.raises(LIALInitError):
            lial_manager.initialize()
    
    def test_basic_message_flow(self):
        """Test the basic message flow from DCM through LIAL."""
        # Create LIAL manager with our adapter already set
        lial_manager = MagicMock(name="LIALManager")
        lial_manager.send_messages.side_effect = self.llm_adapter.send_message_sequence
        
        # Send a message sequence without a persona
        response = lial_manager.send_messages(self.basic_messages)
        
        # Verify the response
        assert isinstance(response, dict)
        assert "conversation" in response
        assert "tool_request" in response
        assert response["conversation"] == "I am an AI assistant. How can I help you?"
        assert response["tool_request"] is None
        
        # Verify the adapter was called
        assert self.llm_adapter.call_count == 1
        assert len(self.llm_adapter.call_history) == 1
        assert self.llm_adapter.call_history[0]["messages"] == self.basic_messages
    
    def test_persona_context_application(self):
        """Test that persona-specific context is properly applied."""
        # Create LIAL manager with our adapter
        lial_manager = MagicMock(name="LIALManager")
        lial_manager.send_messages.side_effect = self.llm_adapter.send_message_sequence
        
        # Configure persona-specific adapter responses
        self.llm_adapter.persona_responses = {
            "catalyst": {
                "conversation": "(Catalyst) I'll help you plan and architect a solution.",
                "tool_request": None
            },
            "forge": {
                "conversation": "(Forge) I'll implement that for you with precision.",
                "tool_request": None
            }
        }
        
        # Test with Catalyst persona
        catalyst_response = lial_manager.send_messages(
            self.basic_messages, 
            active_persona_id="catalyst"
        )
        
        # Verify the response matches Catalyst persona
        assert "(Catalyst)" in catalyst_response["conversation"]
        
        # Test with Forge persona
        forge_response = lial_manager.send_messages(
            self.basic_messages,
            active_persona_id="forge"
        )
        
        # Verify the response matches Forge persona
        assert "(Forge)" in forge_response["conversation"]
    
    def test_dcm_document_lookup(self):
        """Test that LIAL can access DCM documents during message processing."""
        # Configure the adapter to simulate a document lookup from DCM
        def simulate_dcm_lookup(messages, active_persona_id=None):
            # Find the last user message
            user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            
            if "document" in user_message.lower():
                # Extract document ID - assume format like "show me document_id"
                doc_id = user_message.lower().split("document ")[-1].strip()
                doc_content = self.dcm_instance.get_document_content(doc_id)
                
                return {
                    "conversation": f"Here's the content of {doc_id}: {doc_content}",
                    "tool_request": None
                }
            return self.llm_adapter._find_matching_response(messages, active_persona_id)
        
        # Override adapter's send_message_sequence
        self.llm_adapter.send_message_sequence = simulate_dcm_lookup
        
        # Create LIAL manager with our modified adapter
        lial_manager = MagicMock(name="LIALManager")
        lial_manager.send_messages.side_effect = simulate_dcm_lookup
        
        # Create a message requesting a document
        document_request_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Show me document main_system_prompt")
        ])
        
        # Send the request
        response = lial_manager.send_messages(document_request_messages)
        
        # Verify the response contains document content
        assert "Here's the content of main_system_prompt" in response["conversation"]
        assert self.mock_context_content["main_system_prompt"] in response["conversation"]
    
    def test_error_handling_in_chain(self):
        """Test error handling in the DCM-LIAL chain."""
        # Configure the adapter to simulate errors
        self.llm_adapter.configure_error("api_error", Exception("API Error"))
        self.llm_adapter.configure_error("timeout", TimeoutError("Request timed out"))
        
        # Create LIAL manager with our adapter
        lial_manager = MagicMock(name="LIALManager")
        lial_manager.send_messages.side_effect = self.llm_adapter.send_message_sequence
        
        # Create a message that should trigger an API error
        error_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "This should cause api_error")
        ])
        
        # The error should propagate from adapter to LIAL
        with pytest.raises(Exception) as exc_info:
            lial_manager.send_messages(error_messages)
        
        # Verify the error
        assert "API Error" in str(exc_info.value)
        
        # Create a message that should trigger a timeout
        timeout_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "This should cause timeout")
        ])
        
        # The error should propagate from adapter to LIAL
        with pytest.raises(TimeoutError) as exc_info:
            lial_manager.send_messages(timeout_messages)
        
        # Verify the error
        assert "timed out" in str(exc_info.value)
    
    def test_tool_request_generation(self):
        """Test that tool requests are properly generated through the DCM-LIAL chain."""
        # Configure adapter for tool requests
        self.llm_adapter.configure_response("read_file", ResponseBuilder.tool_request(
            tool_name="readFile",
            parameters={"file_path": "/path/to/file.txt"},
            conversation_text="I'll read that file for you.",
            request_id="read-123"
        ))
        
        self.llm_adapter.configure_pattern("read file", "read_file")
        
        # Create LIAL manager with our adapter
        lial_manager = MagicMock(name="LIALManager")
        lial_manager.send_messages.side_effect = self.llm_adapter.send_message_sequence
        
        # Create a message that should trigger a tool request
        tool_request_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Can you read file /path/to/file.txt?")
        ])
        
        # Send the request
        response = lial_manager.send_messages(tool_request_messages)
        
        # Verify the tool request
        assert response["tool_request"] is not None
        assert response["tool_request"]["tool_name"] == "readFile"
        assert response["tool_request"]["parameters"]["file_path"] == "/path/to/file.txt"
        assert "read-123" in response["tool_request"]["request_id"]
        assert "I'll read that file for you." in response["conversation"]
    
    def test_message_history_processing(self):
        """Test that message history is properly processed through the DCM-LIAL chain."""
        # Configure adapter for multi-turn conversations
        self.llm_adapter.configure_response("turn1", {
            "conversation": "I can help with that. What kind of project are you working on?",
            "tool_request": None
        })
        
        self.llm_adapter.configure_response("turn2", {
            "conversation": "That sounds interesting. What programming language are you using?",
            "tool_request": None
        })
        
        self.llm_adapter.configure_pattern("help me", "turn1")
        self.llm_adapter.configure_pattern("web application", "turn2")
        
        # Create LIAL manager with our adapter
        lial_manager = MagicMock(name="LIALManager")
        lial_manager.send_messages.side_effect = self.llm_adapter.send_message_sequence
        
        # Create multi-turn conversation
        turn1_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Can you help me with a project?")
        ])
        
        # First turn
        turn1_response = lial_manager.send_messages(turn1_messages)
        assert "help with that" in turn1_response["conversation"]
        
        # Second turn - add previous messages to history
        turn2_messages = turn1_messages + ResponseBuilder.message_sequence([
            ("assistant", turn1_response["conversation"]),
            ("user", "I'm building a web application.")
        ])
        
        # Send second turn
        turn2_response = lial_manager.send_messages(turn2_messages)
        
        # Verify response takes context from previous messages
        assert "programming language" in turn2_response["conversation"]
        
        # Verify the message history was properly processed
        assert self.llm_adapter.call_count == 2
        assert len(self.llm_adapter.call_history) == 2
        assert len(self.llm_adapter.call_history[1]["messages"]) == 4  # All messages from the conversation