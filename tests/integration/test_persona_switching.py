"""
Integration tests for the persona switching functionality.

These tests verify that the persona switching command works correctly across components.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch, call

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.controller import FrameworkController
from framework_core.exceptions import ComponentInitError
from tests.integration.utils import ResponseBuilder, IntegrationTestCase


class TestPersonaSwitchingIntegration(IntegrationTestCase):
    """
    Integration tests for the persona switching feature.
    
    These tests validate that:
    1. The controller initializes with the correct default persona
    2. The /persona command correctly updates the active persona
    3. The appropriate messages are shown to the user during persona switching
    4. The UI assistant prefix is updated correctly
    5. Subsequent LLM calls use the correct active persona
    """
    
    def test_default_persona_initialization(self, framework_controller_factory):
        """Test that the controller initializes with the default persona from config."""
        # Set up framework settings in the config manager
        config_manager = MagicMock()
        config_manager.get_framework_settings.return_value = {"default_persona": "catalyst"}
        
        # Create a controller with our mock config manager
        controller = framework_controller_factory(config_manager=config_manager)
        
        # Mock the necessary components for _setup_initial_context
        controller.dcm_manager = MagicMock()
        controller.ui_manager = MagicMock()
        
        # Call _setup_initial_context
        controller._setup_initial_context()
        
        # Verify active_persona_id was set to the default from config
        assert controller.active_persona_id == "catalyst"
        
        # Verify UI prefix was updated
        controller.ui_manager.set_assistant_prefix.assert_called_once_with("(Catalyst): ")
    
    def test_persona_command_switching(self, framework_controller_factory):
        """Test that the /persona command switches the active persona."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Set up mock behaviors for components
        persona_definitions = {
            "persona_catalyst": "Catalyst persona content",
            "persona_forge": "Forge persona content"
        }
        controller.dcm_manager.get_persona_definitions.return_value = persona_definitions
        
        # Set initial active persona
        controller.active_persona_id = "catalyst"
        
        # Mock the UI manager's get_user_input to return /persona and then /quit
        controller.ui_manager.get_user_input.side_effect = ["/persona forge", "/quit"]
        
        # Mock the LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am now using the Forge persona.",
            "tool_request": None
        }
        
        # Run the controller (this will process the /persona command)
        controller.run()
        
        # Verify active_persona_id was updated
        assert controller.active_persona_id == "forge"
        
        # Verify UI assistant prefix was updated
        controller.ui_manager.set_assistant_prefix.assert_called_with("(Forge): ")
        
        # Verify success message was displayed
        controller.ui_manager.display_system_message.assert_any_call("Active persona switched to Forge.")
    
    def test_persona_affects_llm_calls(self, framework_controller_factory):
        """Test that the active persona is passed to LLM calls."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Set up a sequence of user inputs to test persona switching and LLM calls
        controller.ui_manager.get_user_input.side_effect = [
            "/persona forge",  # Switch to forge persona
            "Hello",           # Normal user message (should use forge persona)
            "/persona catalyst", # Switch back to catalyst
            "Hello again",     # Normal user message (should use catalyst persona)
            "/quit"
        ]
        
        # Set up mock behavior for persona validation
        persona_definitions = {
            "persona_catalyst": "Catalyst persona content",
            "persona_forge": "Forge persona content"
        }
        controller.dcm_manager.get_persona_definitions.return_value = persona_definitions
        
        # Set up LLM responses
        controller.lial_manager.send_messages.side_effect = [
            # First LLM call (initial response with no user input)
            {"conversation": "Initial response", "tool_request": None},
            # Second LLM call (response after forge persona)
            {"conversation": "Forge response", "tool_request": None},
            # Third LLM call (response after catalyst persona)
            {"conversation": "Catalyst response", "tool_request": None},
        ]
        
        # Run the controller
        controller.run()
        
        # Verify LLM calls with correct personas
        send_messages_calls = controller.lial_manager.send_messages.call_args_list
        
        # First call should use default persona (catalyst)
        assert "active_persona_id" in send_messages_calls[0][1]
        assert send_messages_calls[0][1]["active_persona_id"] == "catalyst"
        
        # Second call should use forge persona
        assert "active_persona_id" in send_messages_calls[1][1]
        assert send_messages_calls[1][1]["active_persona_id"] == "forge"
        
        # Third call should use catalyst persona again
        assert "active_persona_id" in send_messages_calls[2][1]
        assert send_messages_calls[2][1]["active_persona_id"] == "catalyst"
    
    def test_invalid_persona_error_handling(self, framework_controller_factory):
        """Test that trying to switch to an invalid persona shows an error."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Set up mock behaviors
        persona_definitions = {
            "persona_catalyst": "Catalyst persona content",
            "persona_forge": "Forge persona content"
        }
        controller.dcm_manager.get_persona_definitions.return_value = persona_definitions
        
        # Set initial active persona
        controller.active_persona_id = "catalyst"
        
        # Mock user inputs
        controller.ui_manager.get_user_input.side_effect = ["/persona invalid", "/quit"]
        
        # Mock LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify persona was not changed
        assert controller.active_persona_id == "catalyst"
        
        # Verify error message was displayed
        controller.ui_manager.display_error_message.assert_called_once_with(
            "Command Error",
            "Invalid persona ID: invalid. Valid personas: catalyst, forge"
        )
    
    def test_persona_command_without_argument(self, framework_controller_factory):
        """Test that /persona without an argument shows the current persona."""
        # Create and initialize the controller
        controller = framework_controller_factory()
        controller.initialize()
        
        # Set initial active persona
        controller.active_persona_id = "catalyst"
        
        # Mock user inputs
        controller.ui_manager.get_user_input.side_effect = ["/persona", "/quit"]
        
        # Mock LLM response
        controller.lial_manager.send_messages.return_value = {
            "conversation": "I am an AI assistant.",
            "tool_request": None
        }
        
        # Run the controller
        controller.run()
        
        # Verify message showing current persona was displayed
        controller.ui_manager.display_system_message.assert_any_call(
            "Current active persona: Catalyst. Usage: /persona <persona_id>"
        )