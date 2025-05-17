"""
End-to-end tests for basic conversation scenarios.

These tests verify that the framework correctly:
1. Handles basic conversation flows without tool usage
2. Processes messages with proper context retention
3. Correctly applies system messages and personas
4. Manages conversation history
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch, call

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.integration.utils import IntegrationTestCase
from tests.integration.e2e_fixtures import (
    ConversationScenario, 
    MockScenarioBuilder,
    assert_message_count, 
    assert_system_message_added
)


class TestE2EBasicConversation(IntegrationTestCase):
    """
    End-to-end tests for basic conversation scenarios.
    
    These tests verify the framework's ability to handle simple
    user-assistant conversations without tool usage.
    """
    
    def test_single_turn_conversation(self, e2e_controller, mock_conversation, scenario_builder):
        """Test a simple single-turn conversation."""
        # Create a custom scenario for a single turn conversation
        scenario = ConversationScenario(
            name="single_turn",
            description="Single turn conversation"
        ).add_user_input(
            "Hello, can you help me?"
        ).add_expected_llm_response(
            "Hello! I'm the KeystoneAI-Framework assistant. Yes, I can help you with various tasks. What do you need assistance with today?"
        ).add_verification_step(
            lambda controller: assert_message_count(controller, 3),  # System + User + Assistant
            "Verify message count is correct"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify message flow
        controller.message_manager.add_user_message.assert_called_with("Hello, can you help me?")
        controller.message_manager.add_assistant_message.assert_called_with(
            "Hello! I'm the KeystoneAI-Framework assistant. Yes, I can help you with various tasks. What do you need assistance with today?"
        )
        
        # Run verification steps
        for verification_func, description in scenario.verification_steps:
            verification_func(controller)
    
    def test_multi_turn_conversation(self, e2e_controller, mock_conversation, scenario_builder):
        """Test a multi-turn conversation with context retention."""
        # Use the pre-built basic conversation scenario from our builder
        scenario = scenario_builder.create_basic_conversation()
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify the conversation flow
        assert controller.message_manager.add_user_message.call_count == 2
        assert controller.message_manager.add_assistant_message.call_count == 2
        
        # Verify that messages were passed to LLM with context
        assert controller.lial_manager.send_messages.call_count == 2
        
        # Run verification steps
        for verification_func, description in scenario.verification_steps:
            verification_func(controller)
    
    def test_system_message_influence(self, e2e_controller, mock_conversation):
        """Test that system messages properly influence assistant responses."""
        # Create a scenario that tests system message influence
        scenario = ConversationScenario(
            name="system_message_influence",
            description="Testing system message influence on responses"
        ).add_user_input(
            "/system You are a Python expert assistant that always includes code examples."
        ).add_user_input(
            "How do I read a file in Python?"
        ).add_expected_llm_response(
            "To read a file in Python, you can use the built-in `open()` function. Here's an example:\n\n```python\n"
            "# Read entire file content\n"
            "with open('filename.txt', 'r') as file:\n"
            "    content = file.read()\n"
            "    print(content)\n"
            "\n"
            "# Read line by line\n"
            "with open('filename.txt', 'r') as file:\n"
            "    for line in file:\n"
            "        print(line.strip())\n"
            "```\n\n"
            "The `'r'` parameter indicates read mode. You should always use a context manager (`with` statement) "
            "to ensure the file is properly closed after use."
        ).add_verification_step(
            lambda controller: assert_system_message_added(
                controller, 
                "You are a Python expert assistant that always includes code examples."
            ),
            "Verify correct system message was added"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify the system message influenced the response
        assert controller.message_manager.add_system_message.call_count >= 1
        assert controller.message_manager.add_user_message.call_count == 2
        assert controller.message_manager.add_assistant_message.call_count == 1
        
        # Run verification steps
        for verification_func, description in scenario.verification_steps:
            verification_func(controller)
    
    def test_history_pruning(self, e2e_controller, mock_conversation):
        """Test message history pruning during long conversations."""
        # Create a scenario with enough messages to trigger pruning
        scenario = ConversationScenario(
            name="history_pruning",
            description="Testing message history pruning"
        )
        
        # Add 10 exchanges to potentially trigger pruning
        for i in range(10):
            scenario.add_user_input(f"Message {i}")
            scenario.add_expected_llm_response(f"Response to message {i}")
        
        # Configure the message manager to have a small max_length
        e2e_controller.message_manager.config = {"max_length": 5, "pruning_strategy": "remove_oldest"}
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify that pruning was called multiple times
        assert controller.message_manager.prune_history.call_count > 0
    
    def test_persona_context_application(self, e2e_controller, mock_conversation):
        """Test that persona context is correctly applied in conversations."""
        # Configure default persona
        e2e_controller.config_manager.config = {"default_persona": "catalyst"}
        
        # Create a scenario that tests persona-specific responses
        scenario = ConversationScenario(
            name="persona_context",
            description="Testing persona context application"
        ).add_user_input(
            "What's your role?"
        ).add_expected_llm_response(
            "(Catalyst) My role is to help you plan and architect solutions. "
            "I focus on strategic thinking, design, and providing guidance on complex problems."
        )
        
        # Mock the DCM to return persona-specific content
        e2e_controller.dcm_manager.get_persona_definitions.return_value = {
            "catalyst": "# Catalyst Persona\nThe strategic AI planner and architect.",
            "forge": "# Forge Persona\nThe expert AI implementer and system operator."
        }
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify that the persona ID was passed to LIAL
        calls = controller.lial_manager.send_messages.call_args_list
        for call_args in calls:
            args, kwargs = call_args
            assert "active_persona_id" in kwargs
            assert kwargs["active_persona_id"] == "catalyst"
    
    def test_empty_input_handling(self, e2e_controller, mock_conversation):
        """Test handling of empty user input."""
        # Create a scenario with empty input
        scenario = ConversationScenario(
            name="empty_input",
            description="Testing empty input handling"
        ).add_user_input(
            ""  # Empty input
        ).add_user_input(
            "Hello after empty input"
        ).add_expected_llm_response(
            "Hello! How can I assist you today?"
        )
        
        # Set up the controller with our scenario
        controller = mock_conversation(e2e_controller, scenario)
        
        # Run the controller
        controller.run()
        
        # Verify that empty input was properly handled
        # Should only add a message for the second, non-empty input
        assert controller.message_manager.add_user_message.call_count == 1