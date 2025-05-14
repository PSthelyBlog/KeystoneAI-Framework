"""
Central controller for the Framework Core Application.

This module implements the Framework Controller, which orchestrates
the initialization and operation of all components.
"""

from typing import Optional, Dict, Any, List, Tuple

from framework_core.exceptions import (
    ConfigError, 
    DCMInitError, 
    LIALInitError, 
    TEPSInitError,
    ComponentInitError,
    ToolExecutionError
)
from framework_core.component_managers.dcm_manager import DCMManager
from framework_core.component_managers.lial_manager import LIALManager
from framework_core.component_managers.teps_manager import TEPSManager
from framework_core.message_manager import MessageManager
from framework_core.tool_request_handler import ToolRequestHandler
from framework_core.ui_manager import UserInterfaceManager
from framework_core.error_handler import ErrorHandler
from framework_core.utils.logging_utils import setup_logger

class FrameworkController:
    """
    Central orchestrator of the Framework Core Application.
    Manages component initialization, interaction flow, and lifecycle.
    """
    
    # Special commands mapping
    SPECIAL_COMMANDS = {
        "/help": "Show this help message",
        "/quit": "Exit the application",
        "/exit": "Exit the application",
        "/clear": "Clear conversation history",
        "/system": "Add a system message",
        "/debug": "Toggle debug mode"
    }
    
    def __init__(self, config_manager: 'ConfigurationManager'):
        """
        Initialize the Framework Controller with configuration.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.logger = setup_logger("framework_controller")
        self.config_manager = config_manager
        self.dcm_manager = None
        self.lial_manager = None
        self.teps_manager = None
        self.message_manager = None
        self.ui_manager = None
        self.tool_request_handler = None
        self.error_handler = ErrorHandler()
        self.running = False
        self.debug_mode = False
        
    def initialize(self) -> bool:
        """
        Initialize all framework components.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            self.logger.info("Starting Framework Core Application initialization")
            
            # Initialize components in dependency order
            success = self._initialize_dcm()
            if not success:
                return False
                
            success = self._initialize_lial()
            if not success:
                return False
                
            success = self._initialize_teps()
            if not success:
                return False
            
            # Initialize message manager
            self.message_manager = MessageManager(
                config=self.config_manager.get_message_history_settings()
            )
            
            # Initialize UI manager
            self.ui_manager = UserInterfaceManager(
                config=self.config_manager.get_ui_settings()
            )
            
            # Initialize tool request handler
            if not self.teps_manager: # Ensure teps_manager is initialized
                 self.logger.error("TEPS Manager not initialized before ToolRequestHandler.")
                 return False
            self.tool_request_handler = ToolRequestHandler(
                teps_manager=self.teps_manager # Pass the TEPSManager instance
            )
            
            # Set up initial context
            self._setup_initial_context()
            
            self.logger.info("Framework Core Application initialized successfully")
            return True
            
        except Exception as e:
            error_message = self.error_handler.handle_error(
                "Initialization Error", 
                str(e), 
                exception=e
            )
            self.logger.error(f"Initialization failed: {error_message}")
            return False
        
    def _initialize_dcm(self) -> bool:
        """
        Initialize the DCM component.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            context_definition_path = self.config_manager.get_context_definition_path()
            self.logger.info(f"Initializing DCM with context definition: {context_definition_path}")
            
            self.dcm_manager = DCMManager(context_definition_path)
            self.dcm_manager.initialize() # DCMManager's initialize calls DCM's __init__ essentially
            
            self.logger.info("DCM initialization successful")
            return True
            
        except (DCMInitError, ConfigError) as e:
            self.error_handler.handle_error(
                "DCM Initialization Error", 
                str(e), 
                exception=e
            )
            return False
        
    def _initialize_lial(self) -> bool:
        """
        Initialize the LIAL component with the appropriate adapter.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            if not self.dcm_manager:
                raise ComponentInitError("Cannot initialize LIAL: DCM not initialized")
                
            llm_provider = self.config_manager.get_llm_provider()
            # Get LLM settings specific to the active provider
            provider_llm_settings = self.config_manager.get_llm_settings() # This now returns specific settings
            
            self.logger.info(f"Initializing LIAL with provider: {llm_provider}")
            
            self.lial_manager = LIALManager(
                llm_provider=llm_provider,
                llm_settings=provider_llm_settings, # Pass the specific settings
                dcm_manager=self.dcm_manager
            )
            self.lial_manager.initialize()
            
            self.logger.info("LIAL initialization successful")
            return True
            
        except (LIALInitError, ConfigError, ComponentInitError) as e:
            self.error_handler.handle_error(
                "LIAL Initialization Error", 
                str(e), 
                exception=e
            )
            return False
        
    def _initialize_teps(self) -> bool:
        """
        Initialize the TEPS component.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            teps_settings = self.config_manager.get_teps_settings()
            
            self.logger.info("Initializing TEPS")
            
            self.teps_manager = TEPSManager(teps_settings)
            self.teps_manager.initialize()
            
            self.logger.info("TEPS initialization successful")
            return True
            
        except (TEPSInitError, ConfigError) as e:
            self.error_handler.handle_error(
                "TEPS Initialization Error", 
                str(e), 
                exception=e
            )
            return False
            
    def _setup_initial_context(self) -> None:
        """
        Set up the initial context and prompt.
        """
        try:
            # Get initial prompt from DCM
            if not self.dcm_manager:
                self.logger.warning("DCM Manager not initialized, cannot setup initial context.")
                return
            initial_prompt = self.dcm_manager.get_initial_prompt()
            if initial_prompt:
                if not self.message_manager:
                    self.logger.warning("Message Manager not initialized, cannot add initial prompt.")
                    return
                self.message_manager.add_system_message(initial_prompt)
                
            self.logger.info("Initial context setup complete")
            
        except Exception as e:
            self.error_handler.handle_error(
                "Initial Context Setup Error", 
                str(e), 
                exception=e
            )
        
    def run(self) -> None:
        """
        Run the main interaction loop.
        """
        if not self.message_manager or not self.ui_manager or not self.lial_manager:
            error_msg = "Cannot run: core components not initialized (MessageManager, UIManager, or LIALManager)"
            self.logger.error(error_msg)
            # self.ui_manager might be None here, so can't use it to display error directly
            print(f"[CRITICAL ERROR] {error_msg}")
            raise ComponentInitError(error_msg)
        
        self.running = True
        
        # Display welcome message
        welcome_msg = "Framework Core Application started. Type /help for available commands."
        self.ui_manager.display_system_message(welcome_msg)
        
        # Main interaction loop
        while self.running:
            try:
                # Get messages in LLM format
                messages = self.message_manager.get_messages(for_llm=True)
                
                # Send messages to LLM via LIAL
                llm_response = self._process_messages_with_llm(messages)
                
                # Add assistant message to history
                if "conversation" in llm_response and llm_response["conversation"]:
                    assistant_message = llm_response["conversation"]
                    self.message_manager.add_assistant_message(assistant_message)
                    self.ui_manager.display_assistant_message(assistant_message)
                
                # Handle tool requests if present
                if "tool_request" in llm_response and llm_response["tool_request"]:
                    self._handle_tool_request(llm_response["tool_request"])
                    
                    # Continue the conversation without user input if a tool was called
                    continue # This makes the LLM respond to the tool result immediately
                
                # Get user input
                user_input = self.ui_manager.get_user_input()
                
                # Process special commands
                if self._process_special_command(user_input):
                    continue
                
                # Add user message to history if it's not an empty string from Ctrl+C/Ctrl+D
                if user_input:
                    self.message_manager.add_user_message(user_input)
                else: # Handle empty input from Ctrl+C/Ctrl+D which UIManager returns as ""
                    self.logger.info("Empty input received, likely from Ctrl+C/Ctrl+D. Continuing loop.")
                    if not self.running: # if /quit was handled by _process_special_command
                        break
                    continue

                # Prune history if needed
                self.message_manager.prune_history()
                
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
                self.ui_manager.display_system_message("Interrupted. Type /quit to exit.")
            except Exception as e:
                error_message = self.error_handler.handle_error("Runtime Error", str(e), exception=e)
                self.ui_manager.display_error_message("Runtime Error", error_message)
        
        # Perform cleanup
        self.shutdown()
        
    def _process_messages_with_llm(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process messages with the LLM via LIAL.
        
        Args:
            messages: List of messages to send to the LLM
            
        Returns:
            LLMResponse containing conversation and optional tool request
        """
        try:
            self.logger.debug(f"Sending {len(messages)} messages to LLM")
            # Assuming active_persona_id might be managed by the controller or config in future
            active_persona_id = self.config_manager.config.get("default_persona") # Example
            llm_response = self.lial_manager.send_messages(messages, active_persona_id=active_persona_id)
            
            # Validate and sanitize response
            if not isinstance(llm_response, dict):
                self.logger.warning("LLM response is not a dictionary")
                llm_response = {
                    "conversation": "I encountered an issue processing your request. Please try again.",
                    "tool_request": None
                }
            elif "conversation" not in llm_response: # Ensure conversation key exists
                 llm_response["conversation"] = "Received a response without conversational text."


            return llm_response
            
        except Exception as e:
            self.logger.error(f"Error processing messages with LLM: {str(e)}", exc_info=True)
            return {
                "conversation": f"I encountered an error while communicating with the LLM: {str(e)}",
                "tool_request": None
            }
        
    def _handle_tool_request(self, tool_request: Dict[str, Any]) -> None:
        """
        Handle a tool request via the Tool Request Handler.
        
        Args:
            tool_request: The tool request to process
        """
        if not self.tool_request_handler:
            self.logger.error("Tool Request Handler not initialized.")
            # Potentially add an error message to message_manager or display via ui_manager
            return

        try:
            self.logger.info(f"Processing tool request: {tool_request.get('tool_name', 'unknown')}")
            
            # Process the tool request
            tool_result = self.tool_request_handler.process_tool_request(tool_request)
            
            # Format the result as a message
            tool_message_parts = self.tool_request_handler.format_tool_result_as_message(tool_result)
            
            # Add the result to the message history
            self.message_manager.add_tool_result_message(
                tool_name=tool_message_parts["tool_name"],
                content=tool_message_parts["content"], # This is already stringified by format_tool_result_as_message
                tool_call_id=tool_message_parts["tool_call_id"]
            )
            
            if self.debug_mode:
                # In debug mode, display tool result to user
                debug_msg = f"Tool '{tool_message_parts['tool_name']}' executed with result: {tool_message_parts['content'][:200]}..."
                self.ui_manager.display_system_message(debug_msg)
                
        except Exception as e:
            error_message = self.error_handler.handle_error(
                "Tool Execution Error", 
                str(e), 
                exception=e
            )
            self.ui_manager.display_error_message("Tool Execution Error", error_message)
            
            # Add error message to conversation
            error_content = f"Error executing tool '{tool_request.get('tool_name', 'unknown')}': {str(e)}"
            # Ensure tool_request is a dict and has the necessary keys before accessing
            if isinstance(tool_request, dict) and "tool_name" in tool_request and "request_id" in tool_request:
                self.message_manager.add_tool_result_message(
                    tool_name=tool_request["tool_name"],
                    content=error_content, # Error content should be a string
                    tool_call_id=tool_request["request_id"]
                )
            else:
                # Fallback if tool_request structure is unexpected
                self.message_manager.add_tool_result_message(
                    tool_name="unknown_tool_error",
                    content=error_content,
                    tool_call_id="unknown_request_id"
                )

        
    def _process_special_command(self, user_input: str) -> bool:
        """
        Process special commands.
        
        Args:
            user_input: The user input string
            
        Returns:
            True if a special command was processed, False otherwise
        """
        # Ignore empty input from UIManager's default_input_handler (Ctrl+C/Ctrl+D)
        if not user_input:
            return False 
            
        # Check for special commands
        if user_input.startswith("/"):
            command_parts = user_input.split(" ", 1)
            command = command_parts[0].lower()
            
            if command in ["/quit", "/exit"]:
                self.ui_manager.display_system_message("Exiting application...")
                self.running = False
                return True
                
            elif command == "/help":
                self.ui_manager.display_special_command_help(self.SPECIAL_COMMANDS)
                return True
                
            elif command == "/clear":
                self.message_manager.clear_history(preserve_system=True)
                self.ui_manager.display_system_message("Conversation history cleared.")
                return True
                
            elif command == "/system":
                # Add system message
                system_content = command_parts[1].strip() if len(command_parts) > 1 else ""
                if system_content:
                    self.message_manager.add_system_message(system_content)
                    self.ui_manager.display_system_message(f"Added system message: {system_content}")
                else:
                    self.ui_manager.display_error_message("Command Error", "Usage: /system <message_content>")
                return True
                
            elif command == "/debug":
                self.debug_mode = not self.debug_mode
                status = "enabled" if self.debug_mode else "disabled"
                self.ui_manager.display_system_message(f"Debug mode {status}.")
                # Update logger level if debug mode is enabled/disabled
                # This assumes logger setup in utils allows dynamic level changes, or we re-setup loggers.
                # For simplicity, this might require more complex logger management.
                # Example: logging.getLogger().setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
                return True
            else:
                self.ui_manager.display_error_message("Command Error", f"Unknown command: {command}")
                return True # Still processed as a (failed) command
        
        return False
        
    def shutdown(self) -> None:
        """
        Perform graceful shutdown of the framework.
        """
        self.logger.info("Framework shutdown initiated")
        self.running = False
        
        # Cleanup resources if needed (e.g., close network connections, files)
        # LIAL/TEPS/DCM might have their own cleanup methods if necessary in future
        
        self.ui_manager.display_system_message("Framework shutdown complete. Goodbye!")
        self.logger.info("Framework shutdown complete")