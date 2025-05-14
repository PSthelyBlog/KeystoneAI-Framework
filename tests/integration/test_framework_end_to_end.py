#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-end integration tests for the complete framework.

These tests verify that all components of the framework work together correctly
through the entire interaction flow.

AI-GENERATED: [Forge] - Task:[RFI-COREAPP-INT-TEST-001]
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch, call

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the google.generativeai module before importing components
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

from framework_core.config_loader import ConfigurationManager
from framework_core.controller import FrameworkController
from framework_core.message_manager import MessageManager
from framework_core.tool_request_handler import ToolRequestHandler
from framework_core.ui_manager import UserInterfaceManager
from framework_core.dcm import DynamicContextManager
from framework_core.lial_core import LLMAdapterInterface
from framework_core.teps import ToolExecutionService


class MockLLMAdapter(LLMAdapterInterface):
    """Mock LLM Adapter for testing."""
    
    def __init__(self, config: dict, dcm_instance=None) -> None:
        """Initialize the mock adapter."""
        self.config = config
        self.dcm = dcm_instance
        self.message_sequence_history = []
        self.response_queue = []
    
    def send_message_sequence(self, messages: list, active_persona_id: str = None) -> dict:
        """Mock sending messages to LLM, returning predetermined responses."""
        self.message_sequence_history.append({
            'messages': messages,
            'persona_id': active_persona_id
        })
        
        if not self.response_queue:
            # Default response if queue is empty
            return {
                "conversation": "This is a default mock response.",
                "tool_request": None
            }
        
        return self.response_queue.pop(0)
    
    def queue_response(self, response: dict) -> None:
        """Add a predetermined response to the queue."""
        self.response_queue.append(response)


class TestFrameworkEndToEnd(unittest.TestCase):
    """End-to-end integration tests for the framework."""
    
    def setUp(self):
        """Set up test environment with temporary directory and test files."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test context structure
        os.makedirs(os.path.join(self.temp_dir, "system"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "personas"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "config"), exist_ok=True)
        
        # Create sample context file
        with open(os.path.join(self.temp_dir, "FRAMEWORK_CONTEXT.md"), 'w', encoding='utf-8') as f:
            f.write("""# Framework Context Definition

# initial_prompt_template: "You are an AI assistant using the Framework Core Application."

## Personas
persona_test: @./personas/test_persona.md

## Standards
""")
        
        # Create sample persona file
        with open(os.path.join(self.temp_dir, "personas", "test_persona.md"), 'w', encoding='utf-8') as f:
            f.write("# Test Persona\n\nThis is a test persona.")
        
        # Create sample config file
        with open(os.path.join(self.temp_dir, "config", "config.yaml"), 'w', encoding='utf-8') as f:
            f.write("""
llm:
  provider: gemini
  settings:
    api_key: test_key
    model: gemini-1.5-pro
    temperature: 0.7

context:
  definition_path: FRAMEWORK_CONTEXT.md
  default_persona: persona_test

ui:
  use_colors: true
  prompt_symbol: "> "
  
message_history:
  max_messages: 100
  prune_threshold: 120
  
teps:
  allowed_tools: ["read_file", "write_file", "bash"]
  confirmation_required: true
  
logging:
  level: INFO
  file: framework.log
""")
        
        # Create sample system prompt
        with open(os.path.join(self.temp_dir, "system", "main_prompt.md"), 'w', encoding='utf-8') as f:
            f.write("You are an AI assistant using the Framework Core Application.")
        
        # Create real config loader with mock file system
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', create=True) as mock_open:
            # Make file existence checks return True for our config
            mock_exists.return_value = True
            
            # Mock file open to return our config content
            mock_file = MagicMock()
            mock_file.__enter__.return_value.read.return_value = open(os.path.join(self.temp_dir, "config", "config.yaml"), 'r').read()
            mock_open.return_value = mock_file
            
            # Create configuration manager
            self.config = ConfigurationManager()
            self.config.load_configuration(os.path.join(self.temp_dir, "config", "config.yaml"))
        
        # Mock the components we want to isolate
        self.mock_dcm = MagicMock(spec=DynamicContextManager)
        self.mock_dcm.get_initial_prompt_template.return_value = "You are an AI assistant using the Framework Core Application."
        self.mock_dcm.get_document_content.return_value = "This is a test persona."
        
        self.mock_lial_adapter = MockLLMAdapter(self.config.get_llm_settings())
        
        self.mock_teps = MagicMock(spec=ToolExecutionService)
        self.mock_teps.execute_tool.return_value = {
            "request_id": "test_id",
            "tool_name": "test_tool",
            "status": "success",
            "data": {
                "result": "Tool execution successful"
            }
        }
        
        # Create real message manager
        self.message_manager = MessageManager(
            self.config.get_message_history_settings()
        )
        
        # Create real tool request handler with mock TEPS
        self.tool_request_handler = ToolRequestHandler(self.mock_teps)
        
        # Create real UI manager with mock terminal output
        with patch('builtins.print') as self.mock_print:
            self.ui_manager = UserInterfaceManager(
                self.config.get_ui_settings()
            )
        
        # Create a component manager mock for controller
        self.dcm_manager = MagicMock()
        self.dcm_manager.get_dcm_instance.return_value = self.mock_dcm
        
        self.lial_manager = MagicMock()
        self.lial_manager.get_llm_instance.return_value = self.mock_lial_adapter
        self.lial_manager.send_messages.side_effect = self.mock_lial_adapter.send_message_sequence
        
        self.teps_manager = MagicMock()
        self.teps_manager.execute_tool.side_effect = self.mock_teps.execute_tool
        
        # Create controller with managed components
        self.controller = FrameworkController(self.config)
        self.controller.dcm_manager = self.dcm_manager
        self.controller.lial_manager = self.lial_manager
        self.controller.teps_manager = self.teps_manager
        self.controller.message_manager = self.message_manager
        self.controller.ui_manager = self.ui_manager
        self.controller.tool_request_handler = self.tool_request_handler
    
    def tearDown(self):
        """Clean up temporary files and directories."""
        shutil.rmtree(self.temp_dir)
    
    @patch('builtins.input')
    def test_basic_conversation_flow(self, mock_input):
        """Test the basic conversation flow from user input to LLM response."""
        # Setup mock inputs/responses
        mock_input.side_effect = ["Hello, how are you?", "/quit"]
        
        # Queue an LLM response
        self.mock_lial_adapter.queue_response({
            "conversation": "I'm doing well, thank you! How can I assist you today?",
            "tool_request": None
        })
        
        # Run the controller
        self.controller.run()
        
        # Verify system message was displayed
        self.mock_print.assert_any_call("Framework initialized successfully.", color='green')
        
        # Verify user message was displayed
        self.mock_print.assert_any_call("Hello, how are you?", color=None)
        
        # Verify LLM response was displayed
        self.mock_print.assert_any_call("I'm doing well, thank you! How can I assist you today?", color='cyan')
        
        # Verify message history in message manager
        self.assertEqual(len(self.message_manager.messages), 3)  # system + user + assistant
        self.assertEqual(self.message_manager.messages[0]["role"], "system")
        self.assertEqual(self.message_manager.messages[1]["role"], "user")
        self.assertEqual(self.message_manager.messages[1]["content"], "Hello, how are you?")
        self.assertEqual(self.message_manager.messages[2]["role"], "assistant")
        self.assertEqual(self.message_manager.messages[2]["content"], "I'm doing well, thank you! How can I assist you today?")
    
    @patch('builtins.input')
    def test_tool_request_flow(self, mock_input):
        """Test the flow with a tool request from LLM to execution and back."""
        # Setup mock inputs/responses
        mock_input.side_effect = ["Can you check the weather?", "/quit"]
        
        # Queue LLM responses - first with tool request, then with tool result integration
        self.mock_lial_adapter.queue_response({
            "conversation": "I'll check the weather for you.",
            "tool_request": {
                "request_id": "weather_123",
                "tool_name": "check_weather",
                "parameters": {"location": "New York"}
            }
        })
        
        self.mock_lial_adapter.queue_response({
            "conversation": "The weather in New York is sunny and 75°F.",
            "tool_request": None
        })
        
        # Configure mock TEPS response
        self.mock_teps.execute_tool.return_value = {
            "request_id": "weather_123",
            "tool_name": "check_weather",
            "status": "success",
            "data": {
                "result": "Sunny, 75°F"
            }
        }
        
        # Run the controller
        self.controller.run()
        
        # Verify tool request was processed
        self.mock_teps.execute_tool.assert_called_once()
        tool_request_arg = self.mock_teps.execute_tool.call_args[0][0]
        self.assertEqual(tool_request_arg["tool_name"], "check_weather")
        self.assertEqual(tool_request_arg["parameters"]["location"], "New York")
        
        # Verify tool result was added to message history
        tool_messages = [m for m in self.message_manager.messages if m["role"] == "tool_result"]
        self.assertEqual(len(tool_messages), 1)
        self.assertEqual(tool_messages[0]["tool_name"], "check_weather")
        
        # Verify final response incorporating tool result was displayed
        self.mock_print.assert_any_call("The weather in New York is sunny and 75°F.", color='cyan')
    
    @patch('builtins.input')
    def test_special_command_processing(self, mock_input):
        """Test the processing of special commands."""
        # Setup mock inputs
        mock_input.side_effect = ["/help", "/clear", "/debug", "/quit"]
        
        # Run the controller
        self.controller.run()
        
        # Verify help command was processed
        help_calls = [call for call in self.mock_print.call_args_list 
                      if "Available commands" in str(call)]
        self.assertTrue(len(help_calls) > 0)
        
        # Verify clear command was processed
        clear_calls = [call for call in self.mock_print.call_args_list 
                       if "Conversation history cleared" in str(call)]
        self.assertTrue(len(clear_calls) > 0)
        
        # Verify debug command was processed
        debug_calls = [call for call in self.mock_print.call_args_list 
                       if "Debug mode enabled" in str(call)]
        self.assertTrue(len(debug_calls) > 0)
        
        # Verify the controller's debug mode was enabled
        self.assertTrue(self.controller.debug_mode)
    
    @patch('builtins.input')
    def test_error_handling_and_recovery(self, mock_input):
        """Test error handling and recovery during conversation flow."""
        # Setup mock inputs
        mock_input.side_effect = ["Tell me a joke", "What time is it?", "/quit"]
        
        # Queue LLM responses - first normal, then exception, then recovery
        self.mock_lial_adapter.queue_response({
            "conversation": "Why did the chicken cross the road? To get to the other side!",
            "tool_request": None
        })
        
        # Make the second call raise an exception
        original_send = self.mock_lial_adapter.send_message_sequence
        call_count = 0
        
        def side_effect_with_exception(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Second call throws an exception
                raise Exception("LLM API error")
            return original_send(*args, **kwargs)
        
        self.mock_lial_adapter.send_message_sequence = side_effect_with_exception
        self.lial_manager.send_messages.side_effect = side_effect_with_exception
        
        # Queue a recovery response
        self.mock_lial_adapter.queue_response({
            "conversation": "It's currently 3:30 PM.",
            "tool_request": None
        })
        
        # Run the controller with error handling
        self.controller.run()
        
        # Verify first response was processed normally
        self.mock_print.assert_any_call("Why did the chicken cross the road? To get to the other side!", color='cyan')
        
        # Verify error was handled
        error_calls = [call for call in self.mock_print.call_args_list 
                       if "Error communicating with LLM" in str(call)]
        self.assertTrue(len(error_calls) > 0)
        
        # Verify controller recovered and processed the third input
        self.mock_print.assert_any_call("It's currently 3:30 PM.", color='cyan')
    
    @patch('builtins.input')
    def test_multiline_input_processing(self, mock_input):
        """Test processing of multiline input."""
        # Setup mock inputs for multiline
        mock_input.side_effect = ["```", "Line 1", "Line 2", "Line 3", "```", "/quit"]
        
        # Queue LLM response
        self.mock_lial_adapter.queue_response({
            "conversation": "Received your multiline input with 3 lines.",
            "tool_request": None
        })
        
        # Run the controller
        self.controller.run()
        
        # Verify the multiline message was correctly added to history
        user_messages = [m for m in self.message_manager.messages if m["role"] == "user"]
        self.assertEqual(len(user_messages), 1)
        
        expected_content = "Line 1\nLine 2\nLine 3"
        self.assertEqual(user_messages[0]["content"], expected_content)
        
        # Verify LLM received the multiline message
        self.assertEqual(len(self.mock_lial_adapter.message_sequence_history), 1)
        sent_messages = self.mock_lial_adapter.message_sequence_history[0]["messages"]
        
        # Extract user message from sent messages
        user_sent = next((m for m in sent_messages if m["role"] == "user"), None)
        self.assertIsNotNone(user_sent)
        self.assertEqual(user_sent["content"], expected_content)


if __name__ == "__main__":
    unittest.main()