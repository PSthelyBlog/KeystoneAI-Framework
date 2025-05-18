"""
Unit tests for the FrameworkController class in framework_core/controller.py
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import pytest

from framework_core.controller import FrameworkController
from framework_core.exceptions import (
    ConfigError, 
    DCMInitError, 
    LIALInitError, 
    TEPSInitError,
    ComponentInitError,
    ToolExecutionError
)


class TestFrameworkController(unittest.TestCase):
    """Test cases for the FrameworkController class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock for ConfigurationManager
        self.mock_config_manager = Mock()
        
        # Set up common config manager return values
        self.mock_config_manager.get_context_definition_path.return_value = '/path/to/context'
        self.mock_config_manager.get_llm_provider.return_value = 'gemini'
        self.mock_config_manager.get_llm_settings.return_value = {'max_tokens': 1000}
        self.mock_config_manager.get_teps_settings.return_value = {'tools': []}
        self.mock_config_manager.get_message_history_settings.return_value = {'max_messages': 100}
        self.mock_config_manager.get_ui_settings.return_value = {'prompt_prefix': '> '}
        self.mock_config_manager.get_framework_settings.return_value = {'default_persona': 'forge'}
        self.mock_config_manager.config = {'framework': {'default_persona': 'forge'}}
        
        # Initialize controller with mock config manager
        self.controller = FrameworkController(self.mock_config_manager)
        
        # Create mocks for components
        self.mock_dcm_manager = Mock()
        self.mock_lial_manager = Mock()
        self.mock_teps_manager = Mock()
        self.mock_message_manager = Mock()
        self.mock_ui_manager = Mock()
        self.mock_tool_request_handler = Mock()
        self.mock_error_handler = Mock()
        
        # Replace error handler with mock
        self.controller.error_handler = self.mock_error_handler

    def test_initialization(self):
        """Test initialization of FrameworkController."""
        # Verify initial state
        self.assertEqual(self.controller.config_manager, self.mock_config_manager)
        self.assertIsNone(self.controller.dcm_manager)
        self.assertIsNone(self.controller.lial_manager)
        self.assertIsNone(self.controller.teps_manager)
        self.assertIsNone(self.controller.message_manager)
        self.assertIsNone(self.controller.ui_manager)
        self.assertIsNone(self.controller.tool_request_handler)
        self.assertFalse(self.controller.running)
        self.assertFalse(self.controller.debug_mode)
        self.assertIsNone(self.controller.active_persona_id)


    def test_initialize_success(self):
        """Test successful initialization of all components."""
        # Set up mocks for the initialization methods
        with patch.object(self.controller, '_initialize_dcm', return_value=True) as mock_init_dcm, \
             patch.object(self.controller, '_initialize_lial', return_value=True) as mock_init_lial, \
             patch.object(self.controller, '_initialize_teps', return_value=True) as mock_init_teps, \
             patch.object(self.controller, '_setup_initial_context') as mock_setup_context, \
             patch('framework_core.controller.MessageManager') as MockMessageManager, \
             patch('framework_core.controller.UserInterfaceManager') as MockUIManager, \
             patch('framework_core.controller.ToolRequestHandler') as MockToolRequestHandler:
            
            # Configure mocks
            MockMessageManager.return_value = self.mock_message_manager
            MockUIManager.return_value = self.mock_ui_manager
            MockToolRequestHandler.return_value = self.mock_tool_request_handler
            
            # Set up controller state
            self.controller.teps_manager = self.mock_teps_manager
            
            # Call the method under test
            result = self.controller.initialize()
            
            # Verify the result
            self.assertTrue(result)
            
            # Verify method calls
            mock_init_dcm.assert_called_once()
            mock_init_lial.assert_called_once()
            mock_init_teps.assert_called_once()
            mock_setup_context.assert_called_once()
            
            # Verify message manager initialization
            MockMessageManager.assert_called_once_with(
                config=self.mock_config_manager.get_message_history_settings.return_value
            )
            
            # Verify UI manager initialization
            MockUIManager.assert_called_once_with(
                config=self.mock_config_manager.get_ui_settings.return_value
            )
            
            # Verify tool request handler initialization
            MockToolRequestHandler.assert_called_once_with(
                teps_manager=self.mock_teps_manager
            )
            
            # Verify component assignments
            self.assertEqual(self.controller.message_manager, self.mock_message_manager)
            self.assertEqual(self.controller.ui_manager, self.mock_ui_manager)
            self.assertEqual(self.controller.tool_request_handler, self.mock_tool_request_handler)

    def test_initialize_dcm_failure(self):
        """Test initialization failure when DCM initialization fails."""
        # Mock _initialize_dcm to return False
        with patch.object(self.controller, '_initialize_dcm', return_value=False):
            # Call the method under test
            result = self.controller.initialize()
            
            # Verify the result
            self.assertFalse(result)
            
            # Verify that LIAL initialization was not attempted
            self.assertIsNone(self.controller.lial_manager)
            
            # Verify that TEPS initialization was not attempted
            self.assertIsNone(self.controller.teps_manager)

    def test_initialize_lial_failure(self):
        """Test initialization failure when LIAL initialization fails."""
        # Mock _initialize_dcm to return True and _initialize_lial to return False
        with patch.object(self.controller, '_initialize_dcm', return_value=True), \
             patch.object(self.controller, '_initialize_lial', return_value=False):
            
            # Call the method under test
            result = self.controller.initialize()
            
            # Verify the result
            self.assertFalse(result)
            
            # Verify that TEPS initialization was not attempted
            self.assertIsNone(self.controller.teps_manager)

    def test_initialize_teps_failure(self):
        """Test initialization failure when TEPS initialization fails."""
        # Mock _initialize_dcm and _initialize_lial to return True, _initialize_teps to return False
        with patch.object(self.controller, '_initialize_dcm', return_value=True), \
             patch.object(self.controller, '_initialize_lial', return_value=True), \
             patch.object(self.controller, '_initialize_teps', return_value=False):
            
            # Call the method under test
            result = self.controller.initialize()
            
            # Verify the result
            self.assertFalse(result)
            
            # Verify that message manager was not initialized
            self.assertIsNone(self.controller.message_manager)

    def test_initialize_exception(self):
        """Test initialization handles exceptions properly."""
        # Mock an exception during initialization
        with patch.object(self.controller, '_initialize_dcm', side_effect=Exception("Test error")):
            # Call the method under test
            result = self.controller.initialize()
            
            # Verify the result
            self.assertFalse(result)
            
            # Verify error handler was called
            self.mock_error_handler.handle_error.assert_called_once_with(
                "Initialization Error", 
                "Test error", 
                exception=unittest.mock.ANY
            )

    def test_initialize_dcm_success(self):
        """Test successful DCM initialization."""
        # Set up DCMManager mock
        with patch('framework_core.controller.DCMManager') as MockDCMManager:
            MockDCMManager.return_value = self.mock_dcm_manager
            
            # Call the method under test
            result = self.controller._initialize_dcm()
            
            # Verify the result
            self.assertTrue(result)
            
            # Verify DCMManager initialization
            MockDCMManager.assert_called_once_with(self.mock_config_manager.get_context_definition_path.return_value)
            self.mock_dcm_manager.initialize.assert_called_once()
            
            # Verify dcm_manager assignment
            self.assertEqual(self.controller.dcm_manager, self.mock_dcm_manager)

    def test_initialize_dcm_exception(self):
        """Test DCM initialization handles exceptions properly."""
        # Set up DCMManager mock to raise an exception
        with patch('framework_core.controller.DCMManager', side_effect=DCMInitError("DCM init error")):
            # Call the method under test
            result = self.controller._initialize_dcm()
            
            # Verify the result
            self.assertFalse(result)
            
            # Verify error handler was called
            self.mock_error_handler.handle_error.assert_called_once_with(
                "DCM Initialization Error", 
                "DCM init error", 
                exception=unittest.mock.ANY
            )
            
            # Verify dcm_manager is None
            self.assertIsNone(self.controller.dcm_manager)

    def test_initialize_lial_success(self):
        """Test successful LIAL initialization."""
        # Set up dependencies and LIALManager mock
        self.controller.dcm_manager = self.mock_dcm_manager
        
        with patch('framework_core.controller.LIALManager') as MockLIALManager:
            MockLIALManager.return_value = self.mock_lial_manager
            
            # Call the method under test
            result = self.controller._initialize_lial()
            
            # Verify the result
            self.assertTrue(result)
            
            # Verify LIALManager initialization
            MockLIALManager.assert_called_once_with(
                llm_provider=self.mock_config_manager.get_llm_provider.return_value,
                llm_settings=self.mock_config_manager.get_llm_settings.return_value,
                dcm_manager=self.mock_dcm_manager
            )
            self.mock_lial_manager.initialize.assert_called_once()
            
            # Verify lial_manager assignment
            self.assertEqual(self.controller.lial_manager, self.mock_lial_manager)

    def test_initialize_lial_no_dcm(self):
        """Test LIAL initialization fails when DCM is not initialized."""
        # Ensure dcm_manager is None
        self.controller.dcm_manager = None
        
        # Call the method under test
        result = self.controller._initialize_lial()
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify error handler was called with ComponentInitError
        self.mock_error_handler.handle_error.assert_called_once()
        args, _ = self.mock_error_handler.handle_error.call_args
        self.assertEqual(args[0], "LIAL Initialization Error")
        self.assertTrue("Cannot initialize LIAL: DCM not initialized" in args[1])

    def test_initialize_lial_exception(self):
        """Test LIAL initialization handles exceptions properly."""
        # Set up dependencies
        self.controller.dcm_manager = self.mock_dcm_manager
        
        # Set up LIALManager mock to raise an exception
        with patch('framework_core.controller.LIALManager', side_effect=LIALInitError("LIAL init error")):
            # Call the method under test
            result = self.controller._initialize_lial()
            
            # Verify the result
            self.assertFalse(result)
            
            # Verify error handler was called
            self.mock_error_handler.handle_error.assert_called_once_with(
                "LIAL Initialization Error", 
                "LIAL init error", 
                exception=unittest.mock.ANY
            )
            
            # Verify lial_manager is None
            self.assertIsNone(self.controller.lial_manager)

    def test_initialize_teps_success(self):
        """Test successful TEPS initialization."""
        # Set up TEPSManager mock
        with patch('framework_core.controller.TEPSManager') as MockTEPSManager:
            MockTEPSManager.return_value = self.mock_teps_manager
            
            # Call the method under test
            result = self.controller._initialize_teps()
            
            # Verify the result
            self.assertTrue(result)
            
            # Verify TEPSManager initialization
            MockTEPSManager.assert_called_once_with(self.mock_config_manager.get_teps_settings.return_value)
            self.mock_teps_manager.initialize.assert_called_once()
            
            # Verify teps_manager assignment
            self.assertEqual(self.controller.teps_manager, self.mock_teps_manager)

    def test_initialize_teps_exception(self):
        """Test TEPS initialization handles exceptions properly."""
        # Set up TEPSManager mock to raise an exception
        with patch('framework_core.controller.TEPSManager', side_effect=TEPSInitError("TEPS init error")):
            # Call the method under test
            result = self.controller._initialize_teps()
            
            # Verify the result
            self.assertFalse(result)
            
            # Verify error handler was called
            self.mock_error_handler.handle_error.assert_called_once_with(
                "TEPS Initialization Error", 
                "TEPS init error", 
                exception=unittest.mock.ANY
            )
            
            # Verify teps_manager is None
            self.assertIsNone(self.controller.teps_manager)

    def test_setup_initial_context_success(self):
        """Test successful initial context setup."""
        # Set up dependencies
        self.controller.dcm_manager = self.mock_dcm_manager
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        
        # Configure mock return values
        initial_prompt = "This is the initial prompt"
        self.mock_dcm_manager.get_initial_prompt.return_value = initial_prompt
        
        # Call the method under test
        self.controller._setup_initial_context()
        
        # Verify get_initial_prompt was called
        self.mock_dcm_manager.get_initial_prompt.assert_called_once()
        
        # Verify add_system_message was called with the initial prompt
        self.mock_message_manager.add_system_message.assert_called_once_with(initial_prompt)
        
        # Verify active_persona_id was set correctly
        self.assertEqual(self.controller.active_persona_id, "forge")
        
        # Verify UI prefix was updated
        self.mock_ui_manager.set_assistant_prefix.assert_called_once_with("(Forge): ")

    def test_setup_initial_context_no_dcm(self):
        """Test initial context setup when DCM is not initialized."""
        # Ensure dcm_manager is None
        self.controller.dcm_manager = None
        
        # Call the method under test
        self.controller._setup_initial_context()
        
        # Verify no system message was added
        self.mock_message_manager.add_system_message.assert_not_called()

    def test_setup_initial_context_no_message_manager(self):
        """Test initial context setup when MessageManager is not initialized."""
        # Set up DCM but ensure message_manager is None
        self.controller.dcm_manager = self.mock_dcm_manager
        self.controller.message_manager = None
        
        # Configure mock return values
        self.mock_dcm_manager.get_initial_prompt.return_value = "This is the initial prompt"
        
        # Call the method under test
        self.controller._setup_initial_context()
        
        # Verify get_initial_prompt was called
        self.mock_dcm_manager.get_initial_prompt.assert_called_once()
        
        # No assertion for add_system_message since message_manager is None

    def test_setup_initial_context_exception(self):
        """Test initial context setup handles exceptions properly."""
        # Set up dependencies
        self.controller.dcm_manager = self.mock_dcm_manager
        self.controller.message_manager = self.mock_message_manager
        
        # Configure mock to raise an exception
        self.mock_dcm_manager.get_initial_prompt.side_effect = Exception("Context setup error")
        
        # Call the method under test
        self.controller._setup_initial_context()
        
        # Verify error handler was called
        self.mock_error_handler.handle_error.assert_called_once_with(
            "Initial Context Setup Error", 
            "Context setup error", 
            exception=unittest.mock.ANY
        )


    def test_run_components_not_initialized(self):
        """Test run method fails when core components are not initialized."""
        # Ensure core components are None
        self.controller.message_manager = None
        self.controller.ui_manager = None
        self.controller.lial_manager = None
        
        # Call the method under test and expect an exception
        with self.assertRaises(ComponentInitError):
            self.controller.run()
        
        # Verify running flag was not set
        self.assertFalse(self.controller.running)

    def test_run_successful_startup(self):
        """Test run method initializes correctly and shows welcome message."""
        # Set up dependencies
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.lial_manager = self.mock_lial_manager
        
        # Create a mock shutdown function that actually terminates the loop
        def mock_shutdown_impl():
            self.controller.running = False
        
        # Mock welcome message first, then /quit
        call_count = 0
        def process_messages_with_llm_mock(*args):
            return {"conversation": "Initial assistant response", "tool_request": None}
        
        # Force the run method to exit by using "/quit" command
        self.mock_ui_manager.get_user_input.return_value = "/quit"
        
        # Call the method under test
        with patch.object(self.controller, '_process_messages_with_llm', side_effect=process_messages_with_llm_mock) as mock_process, \
             patch.object(self.controller, 'shutdown', side_effect=mock_shutdown_impl) as mock_shutdown:
            # Reset the mock before our test to clear any previous calls
            self.mock_ui_manager.display_system_message.reset_mock()
            self.controller.run()
        
        # Verify welcome message was displayed - using any_call since other messages might be shown first
        self.mock_ui_manager.display_system_message.assert_any_call(
            "Framework Core Application started. Type /help for available commands."
        )
        
        # Verify "Exiting application..." message was displayed
        self.mock_ui_manager.display_system_message.assert_any_call(
            "Exiting application..."
        )
        
        # Verify shutdown was called
        mock_shutdown.assert_called_once()
        
        # Verify running flag was set to False by our mock implementation
        self.assertFalse(self.controller.running)

    def test_run_text_only_response(self):
        """Test run method handles text-only response from LLM."""
        # Set up dependencies
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.lial_manager = self.mock_lial_manager
        self.controller.tool_request_handler = self.mock_tool_request_handler
        
        # Configure mocks for first loop iteration
        messages = [{"role": "user", "content": "Hello"}]
        self.mock_message_manager.get_messages.return_value = messages
        
        # Set up LLM response for text-only response
        llm_response = {
            "conversation": "Hello! How can I help you today?",
            "tool_request": None
        }
        
        # Force the run method to exit after one interaction
        self.mock_ui_manager.get_user_input.side_effect = ["/quit"]
        
        # Mock the _process_messages_with_llm method
        with patch.object(self.controller, '_process_messages_with_llm', return_value=llm_response) as mock_process, \
             patch.object(self.controller, 'shutdown') as mock_shutdown:
            self.controller.run()
        
        # Verify _process_messages_with_llm was called with messages
        mock_process.assert_called_once_with(messages)
        
        # Verify assistant message was added to history
        self.mock_message_manager.add_assistant_message.assert_called_once_with(llm_response["conversation"])
        
        # Verify assistant message was displayed
        self.mock_ui_manager.display_assistant_message.assert_called_once_with(llm_response["conversation"])
        
        # Verify get_user_input was called (exactly once, for the "/quit" command)
        self.mock_ui_manager.get_user_input.assert_called_once()
        
        # Verify shutdown was called
        mock_shutdown.assert_called_once()

    def test_run_tool_request_response(self):
        """Test run method handles tool request response from LLM."""
        # Set up dependencies
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.lial_manager = self.mock_lial_manager
        self.controller.tool_request_handler = self.mock_tool_request_handler
        
        # Configure mocks for loop iterations
        messages = [{"role": "user", "content": "What's the weather?"}]
        self.mock_message_manager.get_messages.return_value = messages
        
        # Set up LLM responses - first with tool request, then with text response
        tool_request = {
            "request_id": "123",
            "tool_name": "weather_tool",
            "parameters": {"location": "New York"}
        }
        
        llm_responses = [
            {
                "conversation": "Let me check the weather for you.",
                "tool_request": tool_request
            },
            {
                "conversation": "It's sunny in New York.",
                "tool_request": None
            }
        ]
        
        # Force the run method to exit after tool execution and response
        self.mock_ui_manager.get_user_input.side_effect = ["/quit"]
        
        # Mock the _process_messages_with_llm method to return the sequence of responses
        with patch.object(self.controller, '_process_messages_with_llm', side_effect=llm_responses) as mock_process, \
             patch.object(self.controller, '_handle_tool_request') as mock_handle_tool, \
             patch.object(self.controller, 'shutdown') as mock_shutdown:
            self.controller.run()
        
        # Verify _process_messages_with_llm was called twice
        self.assertEqual(mock_process.call_count, 2)
        
        # Verify _handle_tool_request was called with the tool request
        mock_handle_tool.assert_called_once_with(tool_request)
        
        # Verify both assistant messages were added to history
        self.mock_message_manager.add_assistant_message.assert_any_call(llm_responses[0]["conversation"])
        self.mock_message_manager.add_assistant_message.assert_any_call(llm_responses[1]["conversation"])
        
        # Verify get_user_input was called only after the final response (exactly once, for the "/quit" command)
        self.mock_ui_manager.get_user_input.assert_called_once()
        
        # Verify shutdown was called
        mock_shutdown.assert_called_once()

    def test_run_exception_in_llm_processing(self):
        """Test run method handles exceptions in LLM processing."""
        # Set up dependencies
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.lial_manager = self.mock_lial_manager
        
        # Configure mocks
        self.mock_message_manager.get_messages.return_value = [{"role": "user", "content": "Hello"}]
        
        # Create a counter to limit exception throwing to avoid infinite loops
        call_count = 0
        
        # Define a function that raises exception only on first call
        def process_with_exception(*args):
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                raise Exception("LLM error")
            return {"conversation": "Response after error", "tool_request": None}
        
        # Create a mock shutdown function that terminates the loop
        def mock_shutdown_impl():
            self.controller.running = False
        
        # Force the run method to exit after handling the exception
        self.mock_ui_manager.get_user_input.return_value = "/quit"
        
        # Mock _process_messages_with_llm to raise an exception only once
        with patch.object(self.controller, '_process_messages_with_llm', side_effect=process_with_exception) as mock_process, \
             patch.object(self.controller, 'shutdown', side_effect=mock_shutdown_impl) as mock_shutdown:
            self.controller.run()
        
        # Verify error message was displayed
        self.mock_ui_manager.display_error_message.assert_called_once_with("Runtime Error", unittest.mock.ANY)
        
        # Verify get_user_input was called (for the "/quit" command)
        self.mock_ui_manager.get_user_input.assert_called_once()
        
        # Verify shutdown was called
        mock_shutdown.assert_called_once()
        
        # Verify running flag was set to False by our mock implementation
        self.assertFalse(self.controller.running)

    def test_run_empty_user_input(self):
        """Test run method handles empty user input (from Ctrl+C/Ctrl+D)."""
        # Set up dependencies
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.lial_manager = self.mock_lial_manager
        
        # Configure mocks for loop iterations
        messages = [{"role": "system", "content": "You are an assistant"}]
        self.mock_message_manager.get_messages.return_value = messages
        
        # Set up LLM response
        llm_response = {
            "conversation": "Hello! How can I help you today?",
            "tool_request": None
        }
        
        # Mock empty input followed by quit command
        self.mock_ui_manager.get_user_input.side_effect = ["", "/quit"]
        
        # Mock methods
        with patch.object(self.controller, '_process_messages_with_llm', return_value=llm_response) as mock_process, \
             patch.object(self.controller, 'shutdown') as mock_shutdown:
            self.controller.run()
        
        # Verify _process_messages_with_llm was called twice (once initially, once after empty input)
        self.assertEqual(mock_process.call_count, 2)
        
        # Verify add_user_message was NOT called for the empty input
        self.mock_message_manager.add_user_message.assert_not_called()
        
        # Verify get_user_input was called twice (once for empty input, once for "/quit")
        self.assertEqual(self.mock_ui_manager.get_user_input.call_count, 2)
        
        # Verify shutdown was called
        mock_shutdown.assert_called_once()

    def test_process_messages_with_llm_success(self):
        """Test _process_messages_with_llm with successful LLM response."""
        # Set up dependencies
        self.controller.lial_manager = self.mock_lial_manager
        
        # Set up test data
        messages = [{"role": "user", "content": "Hello"}]
        llm_response = {
            "conversation": "Hello! How can I help you today?",
            "tool_request": None
        }
        
        # Configure mocks
        self.mock_lial_manager.send_messages.return_value = llm_response
        
        # Set active_persona_id directly for the test
        self.controller.active_persona_id = "forge"
        
        # Call the method under test
        result = self.controller._process_messages_with_llm(messages)
        
        # Verify lial_manager.send_messages was called with the correct arguments
        self.mock_lial_manager.send_messages.assert_called_once_with(
            messages,
            active_persona_id="forge"
        )
        
        # Verify the result matches the expected LLM response
        self.assertEqual(result, llm_response)

    def test_process_messages_with_llm_invalid_response(self):
        """Test _process_messages_with_llm handles invalid LLM response."""
        # Set up dependencies
        self.controller.lial_manager = self.mock_lial_manager
        
        # Set up test data
        messages = [{"role": "user", "content": "Hello"}]
        
        # Configure mock to return a non-dictionary response
        self.mock_lial_manager.send_messages.return_value = "Invalid response"
        
        # Call the method under test
        result = self.controller._process_messages_with_llm(messages)
        
        # Verify result contains fallback response
        self.assertIsInstance(result, dict)
        self.assertIn("conversation", result)
        self.assertIn("tool_request", result)
        self.assertEqual(result["tool_request"], None)
        self.assertTrue("issue processing" in result["conversation"])

    def test_process_messages_with_llm_missing_conversation(self):
        """Test _process_messages_with_llm handles response missing conversation key."""
        # Set up dependencies
        self.controller.lial_manager = self.mock_lial_manager
        
        # Set up test data
        messages = [{"role": "user", "content": "Hello"}]
        
        # Configure mock to return a response without conversation key
        self.mock_lial_manager.send_messages.return_value = {
            "tool_request": None
        }
        
        # Call the method under test
        result = self.controller._process_messages_with_llm(messages)
        
        # Verify result has conversation key added
        self.assertIn("conversation", result)
        self.assertTrue("without conversational text" in result["conversation"])
        self.assertEqual(result["tool_request"], None)

    def test_process_messages_with_llm_exception(self):
        """Test _process_messages_with_llm handles exceptions."""
        # Set up dependencies
        self.controller.lial_manager = self.mock_lial_manager
        
        # Set up test data
        messages = [{"role": "user", "content": "Hello"}]
        
        # Configure mock to raise an exception
        self.mock_lial_manager.send_messages.side_effect = Exception("LLM processing error")
        
        # Call the method under test
        result = self.controller._process_messages_with_llm(messages)
        
        # Verify result contains error response
        self.assertIsInstance(result, dict)
        self.assertIn("conversation", result)
        self.assertIn("tool_request", result)
        self.assertEqual(result["tool_request"], None)
        self.assertTrue("error while communicating with the LLM" in result["conversation"])


    def test_handle_tool_request_success(self):
        """Test successful handling of a tool request."""
        # Set up dependencies
        self.controller.tool_request_handler = self.mock_tool_request_handler
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        
        # Set up test data
        tool_request = {
            "request_id": "123",
            "tool_name": "weather_tool",
            "parameters": {"location": "New York"}
        }
        
        tool_result = {
            "request_id": "123",
            "tool_name": "weather_tool",
            "status": "success",
            "data": {"temperature": 75, "condition": "sunny"}
        }
        
        tool_message_parts = {
            "tool_name": "weather_tool",
            "content": '{"temperature": 75, "condition": "sunny"}',
            "tool_call_id": "123"
        }
        
        # Configure mocks
        self.mock_tool_request_handler.process_tool_request.return_value = tool_result
        self.mock_tool_request_handler.format_tool_result_as_message.return_value = tool_message_parts
        
        # Call the method under test
        self.controller._handle_tool_request(tool_request)
        
        # Verify tool_request_handler.process_tool_request was called with the tool request
        self.mock_tool_request_handler.process_tool_request.assert_called_once_with(tool_request)
        
        # Verify tool_request_handler.format_tool_result_as_message was called with the tool result
        self.mock_tool_request_handler.format_tool_result_as_message.assert_called_once_with(tool_result)
        
        # Verify message_manager.add_tool_result_message was called with the formatted result
        self.mock_message_manager.add_tool_result_message.assert_called_once_with(
            tool_name=tool_message_parts["tool_name"],
            content=tool_message_parts["content"],
            tool_call_id=tool_message_parts["tool_call_id"]
        )
        
        # Verify no debug message was displayed (debug_mode is False by default)
        self.mock_ui_manager.display_system_message.assert_not_called()

    def test_handle_tool_request_with_debug_mode(self):
        """Test handling of a tool request with debug mode enabled."""
        # Set up dependencies
        self.controller.tool_request_handler = self.mock_tool_request_handler
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        
        # Enable debug mode
        self.controller.debug_mode = True
        
        # Set up test data
        tool_request = {
            "request_id": "123",
            "tool_name": "weather_tool",
            "parameters": {"location": "New York"}
        }
        
        tool_result = {
            "request_id": "123",
            "tool_name": "weather_tool",
            "status": "success",
            "data": {"temperature": 75, "condition": "sunny"}
        }
        
        tool_message_parts = {
            "tool_name": "weather_tool",
            "content": '{"temperature": 75, "condition": "sunny"}',
            "tool_call_id": "123"
        }
        
        # Configure mocks
        self.mock_tool_request_handler.process_tool_request.return_value = tool_result
        self.mock_tool_request_handler.format_tool_result_as_message.return_value = tool_message_parts
        
        # Call the method under test
        self.controller._handle_tool_request(tool_request)
        
        # Verify debug message was displayed
        self.mock_ui_manager.display_system_message.assert_called_once()
        
        # Verify debug message contents
        debug_message_call = self.mock_ui_manager.display_system_message.call_args[0][0]
        self.assertTrue("Tool 'weather_tool' executed with result" in debug_message_call)

    def test_handle_tool_request_tool_handler_none(self):
        """Test handling of a tool request when tool_request_handler is None."""
        # Ensure tool_request_handler is None
        self.controller.tool_request_handler = None
        self.controller.ui_manager = self.mock_ui_manager
        
        # Set up test data
        tool_request = {
            "request_id": "123",
            "tool_name": "weather_tool",
            "parameters": {"location": "New York"}
        }
        
        # Call the method under test
        self.controller._handle_tool_request(tool_request)
        
        # No assertions needed as the method should simply return without error

    def test_handle_tool_request_tool_execution_error(self):
        """Test handling of a ToolExecutionError during tool request processing."""
        # Set up dependencies
        self.controller.tool_request_handler = self.mock_tool_request_handler
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.error_handler = self.mock_error_handler
        
        # Set up test data
        tool_request = {
            "request_id": "123",
            "tool_name": "weather_tool",
            "parameters": {"location": "New York"}
        }
        
        error_message = "API connection failed"
        error_result = {
            "status": "error",
            "message": error_message
        }
        
        # Configure mock to raise ToolExecutionError
        self.mock_tool_request_handler.process_tool_request.side_effect = ToolExecutionError(
            error_message, error_result
        )
        
        # Call the method under test
        self.controller._handle_tool_request(tool_request)
        
        # Verify error_handler.handle_error was called
        self.mock_error_handler.handle_error.assert_called_once_with(
            "Tool Execution Error",
            error_message,
            exception=unittest.mock.ANY
        )
        
        # Verify ui_manager.display_error_message was called
        self.mock_ui_manager.display_error_message.assert_called_once_with(
            "Tool Execution Error",
            self.mock_error_handler.handle_error.return_value
        )
        
        # Verify message_manager.add_tool_result_message was called with error content
        self.mock_message_manager.add_tool_result_message.assert_called_once_with(
            tool_name=tool_request["tool_name"],
            content=f"Error executing tool '{tool_request['tool_name']}': {error_message}",
            tool_call_id=tool_request["request_id"]
        )

    def test_handle_tool_request_general_exception(self):
        """Test handling of a general exception during tool request processing."""
        # Set up dependencies
        self.controller.tool_request_handler = self.mock_tool_request_handler
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.error_handler = self.mock_error_handler
        
        # Set up test data
        tool_request = {
            "request_id": "123",
            "tool_name": "weather_tool",
            "parameters": {"location": "New York"}
        }
        
        error_message = "Unexpected error"
        
        # Configure mock to raise a general Exception
        self.mock_tool_request_handler.process_tool_request.side_effect = Exception(error_message)
        
        # Call the method under test
        self.controller._handle_tool_request(tool_request)
        
        # Verify error_handler.handle_error was called
        self.mock_error_handler.handle_error.assert_called_once_with(
            "Tool Execution Error",
            error_message,
            exception=unittest.mock.ANY
        )
        
        # Verify ui_manager.display_error_message was called
        self.mock_ui_manager.display_error_message.assert_called_once_with(
            "Tool Execution Error",
            self.mock_error_handler.handle_error.return_value
        )
        
        # Verify message_manager.add_tool_result_message was called with error content
        self.mock_message_manager.add_tool_result_message.assert_called_once_with(
            tool_name=tool_request["tool_name"],
            content=f"Error executing tool '{tool_request['tool_name']}': {error_message}",
            tool_call_id=tool_request["request_id"]
        )

    def test_handle_tool_request_malformed_request(self):
        """Test handling of a malformed tool request (missing required fields)."""
        # Set up dependencies
        self.controller.tool_request_handler = self.mock_tool_request_handler
        self.controller.message_manager = self.mock_message_manager
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.error_handler = self.mock_error_handler
        
        # Set up malformed tool request (missing request_id and tool_name)
        malformed_request = {
            "parameters": {"location": "New York"}
        }
        
        # Configure mock to raise a general Exception
        error_message = "Tool request is missing required fields"
        self.mock_tool_request_handler.process_tool_request.side_effect = Exception(error_message)
        
        # Call the method under test
        self.controller._handle_tool_request(malformed_request)
        
        # Verify error_handler.handle_error was called
        self.mock_error_handler.handle_error.assert_called_once()
        
        # Verify ui_manager.display_error_message was called
        self.mock_ui_manager.display_error_message.assert_called_once()
        
        # Verify message_manager.add_tool_result_message was called with fallback values
        self.mock_message_manager.add_tool_result_message.assert_called_once()
        call_args = self.mock_message_manager.add_tool_result_message.call_args[1]
        self.assertEqual(call_args["tool_name"], "unknown_tool_error")
        self.assertTrue("Error executing tool" in call_args["content"])
        self.assertEqual(call_args["tool_call_id"], "unknown_request_id")


    def test_process_special_command_empty_input(self):
        """Test processing of empty user input."""
        # Call the method under test
        result = self.controller._process_special_command("")
        
        # Verify result is False (not processed as a special command)
        self.assertFalse(result)

    def test_process_special_command_non_command_input(self):
        """Test processing of regular (non-command) user input."""
        # Call the method under test
        result = self.controller._process_special_command("Hello, how are you?")
        
        # Verify result is False (not processed as a special command)
        self.assertFalse(result)

    def test_process_special_command_quit(self):
        """Test processing of /quit command."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        
        # Call the method under test
        result = self.controller._process_special_command("/quit")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify ui_manager.display_system_message was called with exit message
        self.mock_ui_manager.display_system_message.assert_called_once_with("Exiting application...")
        
        # Verify running flag was set to False
        self.assertFalse(self.controller.running)

    def test_process_special_command_exit(self):
        """Test processing of /exit command."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        
        # Call the method under test
        result = self.controller._process_special_command("/exit")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify ui_manager.display_system_message was called with exit message
        self.mock_ui_manager.display_system_message.assert_called_once_with("Exiting application...")
        
        # Verify running flag was set to False
        self.assertFalse(self.controller.running)

    def test_process_special_command_help(self):
        """Test processing of /help command."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        
        # Call the method under test
        result = self.controller._process_special_command("/help")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify ui_manager.display_special_command_help was called with SPECIAL_COMMANDS
        self.mock_ui_manager.display_special_command_help.assert_called_once_with(self.controller.SPECIAL_COMMANDS)

    def test_process_special_command_clear(self):
        """Test processing of /clear command."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.message_manager = self.mock_message_manager
        
        # Call the method under test
        result = self.controller._process_special_command("/clear")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify message_manager.clear_history was called with preserve_system=True
        self.mock_message_manager.clear_history.assert_called_once_with(preserve_system=True)
        
        # Verify ui_manager.display_system_message was called with cleared message
        self.mock_ui_manager.display_system_message.assert_called_once_with("Conversation history cleared.")

    def test_process_special_command_system_with_content(self):
        """Test processing of /system command with content."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.message_manager = self.mock_message_manager
        
        # Set up system message content
        system_content = "You are a helpful assistant"
        
        # Call the method under test
        result = self.controller._process_special_command(f"/system {system_content}")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify message_manager.add_system_message was called with the system content
        self.mock_message_manager.add_system_message.assert_called_once_with(system_content)
        
        # Verify ui_manager.display_system_message was called with confirmation message
        self.mock_ui_manager.display_system_message.assert_called_once_with(f"Added system message: {system_content}")

    def test_process_special_command_system_without_content(self):
        """Test processing of /system command without content."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.message_manager = self.mock_message_manager
        
        # Call the method under test
        result = self.controller._process_special_command("/system")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify message_manager.add_system_message was NOT called
        self.mock_message_manager.add_system_message.assert_not_called()
        
        # Verify ui_manager.display_error_message was called with usage error
        self.mock_ui_manager.display_error_message.assert_called_once_with(
            "Command Error",
            "Usage: /system <message_content>"
        )

    def test_process_special_command_debug_enable(self):
        """Test processing of /debug command to enable debug mode."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        
        # Ensure debug_mode is initially False
        self.controller.debug_mode = False
        
        # Call the method under test
        result = self.controller._process_special_command("/debug")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify debug_mode was toggled to True
        self.assertTrue(self.controller.debug_mode)
        
        # Verify ui_manager.display_system_message was called with enabled message
        self.mock_ui_manager.display_system_message.assert_called_once_with("Debug mode enabled.")

    def test_process_special_command_debug_disable(self):
        """Test processing of /debug command to disable debug mode."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        
        # Set debug_mode to True initially
        self.controller.debug_mode = True
        
        # Call the method under test
        result = self.controller._process_special_command("/debug")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify debug_mode was toggled to False
        self.assertFalse(self.controller.debug_mode)
        
        # Verify ui_manager.display_system_message was called with disabled message
        self.mock_ui_manager.display_system_message.assert_called_once_with("Debug mode disabled.")

    def test_process_special_command_persona_valid(self):
        """Test processing of /persona command with valid persona."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.dcm_manager = self.mock_dcm_manager
        self.controller.active_persona_id = "catalyst"
        
        # Configure mock to return valid personas
        self.mock_dcm_manager.get_persona_definitions.return_value = {
            "persona_catalyst": "Catalyst persona content",
            "persona_forge": "Forge persona content"
        }
        
        # Call the method under test
        result = self.controller._process_special_command("/persona forge")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify persona was updated
        self.assertEqual(self.controller.active_persona_id, "forge")
        
        # Verify UI prefix was updated
        self.mock_ui_manager.set_assistant_prefix.assert_called_once_with("(Forge): ")
        
        # Verify success message was displayed
        self.mock_ui_manager.display_system_message.assert_called_once_with("Active persona switched to Forge.")
        
    def test_process_special_command_persona_invalid(self):
        """Test processing of /persona command with invalid persona."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.dcm_manager = self.mock_dcm_manager
        self.controller.active_persona_id = "catalyst"
        
        # Configure mock to return valid personas
        self.mock_dcm_manager.get_persona_definitions.return_value = {
            "persona_catalyst": "Catalyst persona content",
            "persona_forge": "Forge persona content"
        }
        
        # Call the method under test
        result = self.controller._process_special_command("/persona invalid")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify persona was not updated
        self.assertEqual(self.controller.active_persona_id, "catalyst")
        
        # Verify error message was displayed
        self.mock_ui_manager.display_error_message.assert_called_once_with(
            "Command Error",
            "Invalid persona ID: invalid. Valid personas: catalyst, forge"
        )
        
    def test_process_special_command_persona_without_argument(self):
        """Test processing of /persona command without argument."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        self.controller.active_persona_id = "catalyst"
        
        # Call the method under test
        result = self.controller._process_special_command("/persona")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify display message was shown
        self.mock_ui_manager.display_system_message.assert_called_once_with(
            "Current active persona: Catalyst. Usage: /persona <persona_id>"
        )
        
    def test_process_special_command_unknown(self):
        """Test processing of unknown special command."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        
        # Call the method under test with an unknown command
        result = self.controller._process_special_command("/unknown")
        
        # Verify result is True (processed as a special command)
        self.assertTrue(result)
        
        # Verify ui_manager.display_error_message was called with unknown command error
        self.mock_ui_manager.display_error_message.assert_called_once_with(
            "Command Error",
            "Unknown command: /unknown"
        )


    def test_shutdown(self):
        """Test graceful shutdown of the framework."""
        # Set up dependencies
        self.controller.ui_manager = self.mock_ui_manager
        
        # Set running flag to True
        self.controller.running = True
        
        # Call the method under test
        self.controller.shutdown()
        
        # Verify running flag was set to False
        self.assertFalse(self.controller.running)
        
        # Verify ui_manager.display_system_message was called with shutdown message
        self.mock_ui_manager.display_system_message.assert_called_once_with(
            "Framework shutdown complete. Goodbye!"
        )

