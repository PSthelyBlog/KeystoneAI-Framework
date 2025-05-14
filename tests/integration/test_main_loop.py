"""
Integration tests for the Framework Core Application main loop.
"""

import unittest
from unittest.mock import patch, MagicMock

from framework_core.config_loader import ConfigurationManager
from framework_core.controller import FrameworkController
from framework_core.message_manager import MessageManager
from framework_core.tool_request_handler import ToolRequestHandler
from framework_core.ui_manager import UserInterfaceManager

class TestMainLoop(unittest.TestCase):
    """Test cases for the main interaction loop."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock configuration manager
        self.mock_config = MagicMock()
        self.mock_config.get_llm_provider.return_value = "test_provider"
        self.mock_config.get_llm_settings.return_value = {}
        self.mock_config.get_context_definition_path.return_value = "./test_context.md"
        self.mock_config.get_teps_settings.return_value = {}
        self.mock_config.get_message_history_settings.return_value = {}
        self.mock_config.get_ui_settings.return_value = {}
        
        # Create controller with mocked config
        self.controller = FrameworkController(self.mock_config)
        
        # Mock component managers
        self.controller.dcm_manager = MagicMock()
        self.controller.dcm_manager.get_initial_prompt.return_value = "Initial prompt"
        
        self.controller.lial_manager = MagicMock()
        self.controller.lial_manager.send_messages.return_value = {
            "conversation": "Assistant response",
            "tool_request": None
        }
        
        self.controller.teps_manager = MagicMock()
        
        # Create real message manager
        self.controller.message_manager = MessageManager()
        
        # Mock UI manager
        self.controller.ui_manager = MagicMock()
        
        # Create real tool request handler with mocked TEPS
        self.controller.tool_request_handler = ToolRequestHandler(self.controller.teps_manager)
        
    @patch.object(FrameworkController, '_process_messages_with_llm')
    @patch.object(FrameworkController, '_process_special_command')
    def test_main_loop_basic_interaction(self, mock_process_command, mock_process_llm):
        """Test basic interaction flow in the main loop."""
        # Configure mocks
        mock_process_llm.return_value = {
            "conversation": "Assistant response",
            "tool_request": None
        }
        mock_process_command.return_value = False  # Not a special command
        
        # Mock user input to first provide input then terminate
        self.controller.ui_manager.get_user_input.side_effect = ["Test user input", KeyboardInterrupt(), "/quit"]
        
        # Run the controller
        self.controller.run()
        
        # Verify initial setup
        self.controller.ui_manager.display_system_message.assert_called()
        
        # Verify user input was processed
        self.assertEqual(len(self.controller.message_manager.messages), 3)  # Initial + user + assistant
        
        # Verify LLM was called with messages
        mock_process_llm.assert_called()
        
        # Verify special command processing was attempted
        mock_process_command.assert_called_with("Test user input")
        
        # Verify assistant message was displayed
        self.controller.ui_manager.display_assistant_message.assert_called_with("Assistant response")
        
    @patch.object(FrameworkController, '_handle_tool_request')
    def test_main_loop_with_tool_request(self, mock_handle_tool):
        """Test interaction flow with tool requests."""
        # Configure LIAL to return a tool request then a normal response
        self.controller.lial_manager.send_messages.side_effect = [
            {
                "conversation": "I'll help with that",
                "tool_request": {
                    "request_id": "req123",
                    "tool_name": "test_tool",
                    "parameters": {}
                }
            },
            {
                "conversation": "Here's the result",
                "tool_request": None
            }
        ]
        
        # Mock user input to provide input then terminate
        self.controller.ui_manager.get_user_input.side_effect = ["/quit"]
        
        # Run the controller
        self.controller.run()
        
        # Verify tool request was handled
        mock_handle_tool.assert_called_once()
        
    def test_process_special_commands(self):
        """Test processing of special commands."""
        # Test /help command
        self.assertTrue(self.controller._process_special_command("/help"))
        self.controller.ui_manager.display_special_command_help.assert_called_once()
        
        # Test /clear command
        self.controller.ui_manager.reset_mock()
        self.assertTrue(self.controller._process_special_command("/clear"))
        self.controller.ui_manager.display_system_message.assert_called_once()
        
        # Test /quit command
        self.controller.ui_manager.reset_mock()
        self.assertTrue(self.controller._process_special_command("/quit"))
        self.assertFalse(self.controller.running)
        
        # Test /debug command
        self.controller.ui_manager.reset_mock()
        self.controller.running = True  # Reset for test
        self.assertTrue(self.controller._process_special_command("/debug"))
        self.assertTrue(self.controller.debug_mode)
        
        # Test non-command
        self.controller.ui_manager.reset_mock()
        self.assertFalse(self.controller._process_special_command("normal message"))
        
    def test_handle_tool_request(self):
        """Test handling of tool requests."""
        # Mock TEPS to return a successful result
        self.controller.teps_manager.execute_tool.return_value = {
            "request_id": "req123",
            "tool_name": "test_tool",
            "status": "success",
            "data": {
                "result": "Tool execution successful"
            }
        }
        
        # Create a test tool request
        tool_request = {
            "request_id": "req123",
            "tool_name": "test_tool",
            "parameters": {}
        }
        
        # Handle the request
        self.controller._handle_tool_request(tool_request)
        
        # Verify TEPS was called
        self.controller.teps_manager.execute_tool.assert_called_once_with(tool_request)
        
        # Verify message was added to history
        tool_messages = [m for m in self.controller.message_manager.messages if m["role"] == "tool_result"]
        self.assertEqual(len(tool_messages), 1)
        self.assertEqual(tool_messages[0]["tool_name"], "test_tool")

if __name__ == "__main__":
    unittest.main()