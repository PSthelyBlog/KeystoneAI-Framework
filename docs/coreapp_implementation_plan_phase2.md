# Implementation Plan: Framework Core Application - Phase 2

**Date:** 2025-05-13  
**Plan ID:** IMPL-COREAPP-PHASE2  
**Related RFI:** RFI-COREAPP-IMPL-002  
**Author:** Catalyst

## 1. Overview

This implementation plan provides a detailed, step-by-step approach for implementing Phase 2 of the Framework Core Application, focusing on the Message Manager, Tool Request Handler, User Interface Manager, and the main interaction loop, as outlined in RFI-COREAPP-IMPL-002. The plan breaks down the work into logical steps, each with specific tasks, dependencies, and implementation guidelines.

## 2. Implementation Steps

### Step 1: Message Manager Implementation

**Objective:** Implement the Message Manager component to handle conversation history.

**Tasks:**

1. Create the message_manager.py file with the MessageManager class:
   ```python
   """
   Message management for the Framework Core Application.
   
   This module handles the conversation history and message pruning capabilities.
   """
   
   from typing import List, Dict, Any, Optional, Literal
   import json
   import time
   from copy import deepcopy
   
   from framework_core.utils.logging_utils import setup_logger
   
   class MessageManager:
       """
       Manages conversation history and provides message pruning capabilities.
       """
       
       def __init__(self, config: Optional[Dict[str, Any]] = None):
           """
           Initialize the Message Manager.
           
           Args:
               config: Optional configuration dictionary
           """
           self.logger = setup_logger("message_manager")
           self.config = config or {}
           self.messages = []
           self.max_history_length = self.config.get("max_length", 100)
           self.pruning_strategy = self.config.get("pruning_strategy", "remove_oldest")
           self.prioritize_system_messages = self.config.get("prioritize_system_messages", True)
           
       def add_system_message(self, content: str) -> None:
           """
           Add a system message to the conversation history.
           
           Args:
               content: The message content
           """
           self.messages.append({
               "role": "system",
               "content": content,
               "timestamp": time.time()
           })
           self.logger.debug(f"Added system message: {content[:50]}...")
           
       def add_user_message(self, content: str) -> None:
           """
           Add a user message to the conversation history.
           
           Args:
               content: The message content
           """
           self.messages.append({
               "role": "user",
               "content": content,
               "timestamp": time.time()
           })
           self.logger.debug(f"Added user message: {content[:50]}...")
           
       def add_assistant_message(self, content: str) -> None:
           """
           Add an assistant message to the conversation history.
           
           Args:
               content: The message content
           """
           self.messages.append({
               "role": "assistant",
               "content": content,
               "timestamp": time.time()
           })
           self.logger.debug(f"Added assistant message: {content[:50]}...")
           
       def add_tool_result_message(
           self, 
           tool_name: str, 
           content: Any, 
           tool_call_id: str
       ) -> None:
           """
           Add a tool result message to the conversation history.
           
           Args:
               tool_name: The name of the tool
               content: The tool result content
               tool_call_id: The ID of the tool call
           """
           # Convert non-string content to JSON
           if not isinstance(content, str):
               try:
                   content = json.dumps(content)
               except Exception as e:
                   self.logger.warning(f"Failed to serialize tool result: {str(e)}")
                   content = str(content)
                   
           self.messages.append({
               "role": "tool_result",
               "content": content,
               "tool_name": tool_name,
               "tool_call_id": tool_call_id,
               "timestamp": time.time()
           })
           self.logger.debug(f"Added tool result for {tool_name}: {content[:50]}...")
           
       def get_messages(
           self, 
           include_roles: Optional[List[str]] = None,
           exclude_roles: Optional[List[str]] = None,
           for_llm: bool = False
       ) -> List[Dict[str, Any]]:
           """
           Get messages from the conversation history with optional filtering.
           
           Args:
               include_roles: Optional list of roles to include
               exclude_roles: Optional list of roles to exclude
               for_llm: Whether to format messages for LLM consumption
               
           Returns:
               List of message dictionaries
           """
           # Filter messages by role if specified
           filtered_messages = self.messages
           
           if include_roles:
               filtered_messages = [m for m in filtered_messages if m.get("role") in include_roles]
               
           if exclude_roles:
               filtered_messages = [m for m in filtered_messages if m.get("role") not in exclude_roles]
               
           # Format for LLM if requested
           if for_llm:
               return self._format_for_llm(filtered_messages)
               
           return deepcopy(filtered_messages)
           
       def _format_for_llm(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
           """
           Format messages for LLM consumption.
           
           Args:
               messages: List of messages to format
               
           Returns:
               Formatted message list
           """
           formatted_messages = []
           
           for msg in messages:
               role = msg.get("role")
               content = msg.get("content")
               
               if role == "tool_result":
                   # Format tool results according to LLM API requirements
                   formatted_messages.append({
                       "role": "tool",
                       "content": content,
                       "name": msg.get("tool_name"),
                       "tool_call_id": msg.get("tool_call_id")
                   })
               else:
                   # Standard message roles (system, user, assistant)
                   formatted_messages.append({
                       "role": role,
                       "content": content
                   })
                   
           return formatted_messages
           
       def prune_history(self, preserve_system: bool = True) -> None:
           """
           Prune the message history to prevent context window overflow.
           
           Args:
               preserve_system: Whether to preserve system messages
           """
           if len(self.messages) <= self.max_history_length:
               return
               
           self.logger.info(f"Pruning message history from {len(self.messages)} messages")
           
           if self.pruning_strategy == "remove_oldest":
               if preserve_system and self.prioritize_system_messages:
                   # Separate system messages
                   system_messages = [m for m in self.messages if m.get("role") == "system"]
                   non_system_messages = [m for m in self.messages if m.get("role") != "system"]
                   
                   # Keep only the most recent non-system messages
                   max_non_system = self.max_history_length - len(system_messages)
                   if max_non_system > 0:
                       non_system_messages = sorted(
                           non_system_messages, 
                           key=lambda m: m.get("timestamp", 0),
                           reverse=True
                       )[:max_non_system]
                       
                   # Combine and sort by timestamp
                   self.messages = system_messages + non_system_messages
                   self.messages.sort(key=lambda m: m.get("timestamp", 0))
               else:
                   # Simple truncation keeping most recent messages
                   self.messages = sorted(
                       self.messages,
                       key=lambda m: m.get("timestamp", 0),
                       reverse=True
                   )[:self.max_history_length]
                   self.messages.sort(key=lambda m: m.get("timestamp", 0))
           
           elif self.pruning_strategy == "summarize":
               # Placeholder for future summarization logic
               # For now, fall back to remove_oldest
               self.logger.warning("Summarization not yet implemented, falling back to remove_oldest")
               self.pruning_strategy = "remove_oldest"
               self.prune_history(preserve_system)
               
           self.logger.info(f"Pruned message history to {len(self.messages)} messages")
           
       def clear_history(self, preserve_system: bool = True) -> None:
           """
           Clear the message history.
           
           Args:
               preserve_system: Whether to preserve system messages
           """
           if preserve_system:
               self.messages = [msg for msg in self.messages if msg.get("role") == "system"]
               self.logger.info(f"Cleared non-system messages, {len(self.messages)} system messages preserved")
           else:
               self.messages = []
               self.logger.info("Cleared all messages")
               
       def serialize(self) -> Dict[str, Any]:
           """
           Serialize the message history for storage.
           
           Returns:
               Dictionary representation of the message history
           """
           return {
               "messages": deepcopy(self.messages),
               "max_history_length": self.max_history_length,
               "pruning_strategy": self.pruning_strategy,
               "prioritize_system_messages": self.prioritize_system_messages
           }
           
       def deserialize(self, data: Dict[str, Any]) -> None:
           """
           Deserialize stored message history.
           
           Args:
               data: Dictionary representation of message history
           """
           if not isinstance(data, dict):
               self.logger.error("Invalid deserialization data format")
               return
               
           self.messages = data.get("messages", [])
           self.max_history_length = data.get("max_history_length", self.max_history_length)
           self.pruning_strategy = data.get("pruning_strategy", self.pruning_strategy)
           self.prioritize_system_messages = data.get(
               "prioritize_system_messages", 
               self.prioritize_system_messages
           )
           
           self.logger.info(f"Deserialized {len(self.messages)} messages")
   ```

2. Implement unit tests for the MessageManager class:
   ```python
   """
   Unit tests for the Message Manager.
   """
   
   import unittest
   import time
   from unittest.mock import patch, MagicMock
   
   from framework_core.message_manager import MessageManager
   
   class TestMessageManager(unittest.TestCase):
       """Test cases for MessageManager."""
       
       def setUp(self):
           """Set up test fixtures."""
           self.config = {
               "max_length": 10,
               "pruning_strategy": "remove_oldest",
               "prioritize_system_messages": True
           }
           self.manager = MessageManager(self.config)
           
       def test_add_messages(self):
           """Test adding different types of messages."""
           self.manager.add_system_message("System message")
           self.manager.add_user_message("User message")
           self.manager.add_assistant_message("Assistant message")
           self.manager.add_tool_result_message("test_tool", "Tool result", "tool_call_123")
           
           messages = self.manager.get_messages()
           self.assertEqual(len(messages), 4)
           
           roles = [msg["role"] for msg in messages]
           self.assertIn("system", roles)
           self.assertIn("user", roles)
           self.assertIn("assistant", roles)
           self.assertIn("tool_result", roles)
           
       def test_get_messages_filtering(self):
           """Test filtering messages by role."""
           self.manager.add_system_message("System message")
           self.manager.add_user_message("User message")
           self.manager.add_assistant_message("Assistant message")
           
           # Include only specific roles
           filtered = self.manager.get_messages(include_roles=["user", "assistant"])
           self.assertEqual(len(filtered), 2)
           roles = [msg["role"] for msg in filtered]
           self.assertNotIn("system", roles)
           
           # Exclude specific roles
           filtered = self.manager.get_messages(exclude_roles=["system"])
           self.assertEqual(len(filtered), 2)
           roles = [msg["role"] for msg in filtered]
           self.assertNotIn("system", roles)
           
       def test_format_for_llm(self):
           """Test formatting messages for LLM consumption."""
           self.manager.add_system_message("System message")
           self.manager.add_user_message("User message")
           self.manager.add_tool_result_message("test_tool", "Tool result", "tool_call_123")
           
           llm_messages = self.manager.get_messages(for_llm=True)
           
           # Check tool result format
           tool_msg = [m for m in llm_messages if m.get("role") == "tool"][0]
           self.assertEqual(tool_msg["name"], "test_tool")
           self.assertEqual(tool_msg["tool_call_id"], "tool_call_123")
           
       def test_prune_history_preserve_system(self):
           """Test pruning history while preserving system messages."""
           # Add more messages than max_length
           self.manager.add_system_message("System message 1")
           self.manager.add_system_message("System message 2")
           
           # Add non-system messages with artificial timestamp delay
           for i in range(10):
               self.manager.add_user_message(f"User message {i}")
               self.manager.messages[-1]["timestamp"] = time.time() + i
               
           # Should be 12 messages total now
           self.assertEqual(len(self.manager.messages), 12)
           
           # Prune
           self.manager.prune_history(preserve_system=True)
           
           # Should keep all system messages (2) and up to 8 non-system messages
           self.assertEqual(len(self.manager.messages), 10)
           
           # Check system messages were preserved
           system_count = sum(1 for m in self.manager.messages if m["role"] == "system")
           self.assertEqual(system_count, 2)
           
       def test_clear_history(self):
           """Test clearing history with and without preserving system messages."""
           self.manager.add_system_message("System message")
           self.manager.add_user_message("User message")
           self.manager.add_assistant_message("Assistant message")
           
           # Clear with system preservation
           self.manager.clear_history(preserve_system=True)
           self.assertEqual(len(self.manager.messages), 1)
           self.assertEqual(self.manager.messages[0]["role"], "system")
           
           # Add more and clear without preservation
           self.manager.add_user_message("User message")
           self.manager.clear_history(preserve_system=False)
           self.assertEqual(len(self.manager.messages), 0)
           
       def test_serialize_deserialize(self):
           """Test serialization and deserialization."""
           self.manager.add_system_message("System message")
           self.manager.add_user_message("User message")
           
           serialized = self.manager.serialize()
           
           # Create new manager and deserialize
           new_manager = MessageManager()
           new_manager.deserialize(serialized)
           
           # Check messages were preserved
           self.assertEqual(len(new_manager.messages), 2)
           roles = [msg["role"] for msg in new_manager.messages]
           self.assertIn("system", roles)
           self.assertIn("user", roles)
           
           # Check settings were preserved
           self.assertEqual(new_manager.max_history_length, 10)
           self.assertEqual(new_manager.pruning_strategy, "remove_oldest")
           self.assertTrue(new_manager.prioritize_system_messages)
   ```

**Dependencies:** Phase 1 components

**Time Estimate:** 90 minutes

---

### Step 2: Tool Request Handler Implementation

**Objective:** Implement the Tool Request Handler component to process and execute tool requests via TEPS.

**Tasks:**

1. Create the tool_request_handler.py file with the ToolRequestHandler class:
   ```python
   """
   Tool request handling for the Framework Core Application.
   
   This module processes tool requests and manages the tool execution flow via TEPS.
   """
   
   import json
   from typing import Dict, Any, List, Optional, Union
   
   from framework_core.utils.logging_utils import setup_logger
   from framework_core.exceptions import ToolExecutionError
   
   class ToolRequestHandler:
       """
       Processes tool requests and manages tool execution flow via TEPS.
       """
       
       def __init__(self, teps_manager: 'TEPSManager'):
           """
           Initialize the Tool Request Handler.
           
           Args:
               teps_manager: The TEPS manager instance
           """
           self.logger = setup_logger("tool_request_handler")
           self.teps_manager = teps_manager
           
       def process_tool_request(
           self, 
           tool_request: Dict[str, Any]
       ) -> Dict[str, Any]:
           """
           Process a tool request via TEPS.
           
           Args:
               tool_request: The tool request to process
               
           Returns:
               A ToolResult containing the result of the tool execution
               
           Raises:
               ToolExecutionError: If tool execution fails
           """
           self.logger.info(f"Processing tool request for {tool_request.get('tool_name', 'unknown')}")
           
           # Validate the tool request
           self._validate_tool_request(tool_request)
           
           try:
               # Execute the tool via TEPS
               tool_result = self.teps_manager.execute_tool(tool_request)
               
               self.logger.info(f"Tool execution completed with status: {tool_result.get('status', 'unknown')}")
               return tool_result
               
           except Exception as e:
               self.logger.error(f"Tool execution failed: {str(e)}")
               
               # Create error result
               error_result = {
                   "request_id": tool_request.get("request_id", "unknown"),
                   "tool_name": tool_request.get("tool_name", "unknown"),
                   "status": "error",
                   "data": {
                       "error_message": str(e)
                   }
               }
               
               raise ToolExecutionError(str(e), error_result)
           
       def process_batch_tool_requests(
           self, 
           tool_requests: List[Dict[str, Any]]
       ) -> List[Dict[str, Any]]:
           """
           Process multiple tool requests in batch.
           
           Args:
               tool_requests: List of tool requests to process
               
           Returns:
               List of tool results
           """
           self.logger.info(f"Processing batch of {len(tool_requests)} tool requests")
           
           results = []
           
           for request in tool_requests:
               try:
                   result = self.process_tool_request(request)
                   results.append(result)
               except ToolExecutionError as e:
                   # Add error result to results list
                   if hasattr(e, 'error_result'):
                       results.append(e.error_result)
                   else:
                       # Fallback error result
                       results.append({
                           "request_id": request.get("request_id", "unknown"),
                           "tool_name": request.get("tool_name", "unknown"),
                           "status": "error",
                           "data": {
                               "error_message": str(e)
                           }
                       })
                       
           return results
           
       def _validate_tool_request(self, tool_request: Dict[str, Any]) -> None:
           """
           Validate a tool request before processing.
           
           Args:
               tool_request: The tool request to validate
               
           Raises:
               ValueError: If tool request is invalid
           """
           # Check required fields
           required_fields = ["tool_name", "parameters"]
           for field in required_fields:
               if field not in tool_request:
                   raise ValueError(f"Tool request missing required field: {field}")
                   
           # Check tool_name is a string
           if not isinstance(tool_request["tool_name"], str):
               raise ValueError("tool_name must be a string")
               
           # Check parameters is a dict
           if not isinstance(tool_request["parameters"], dict):
               raise ValueError("parameters must be a dictionary")
               
       def format_tool_result_as_message(
           self, 
           tool_result: Dict[str, Any]
       ) -> Dict[str, Any]:
           """
           Format a tool result as a message for the conversation history.
           
           Args:
               tool_result: The tool result to format
               
           Returns:
               Formatted message
           """
           content = tool_result.get("data", {})
           
           # Convert content to string if needed
           if not isinstance(content, str):
               try:
                   content = json.dumps(content)
               except Exception as e:
                   self.logger.warning(f"Failed to serialize tool result: {str(e)}")
                   content = str(content)
                   
           return {
               "role": "tool_result",
               "content": content,
               "tool_name": tool_result.get("tool_name", "unknown"),
               "tool_call_id": tool_result.get("request_id", "unknown")
           }
   ```

2. Implement unit tests for the ToolRequestHandler class:
   ```python
   """
   Unit tests for the Tool Request Handler.
   """
   
   import unittest
   from unittest.mock import patch, MagicMock
   
   from framework_core.tool_request_handler import ToolRequestHandler
   from framework_core.exceptions import ToolExecutionError
   
   class TestToolRequestHandler(unittest.TestCase):
       """Test cases for ToolRequestHandler."""
       
       def setUp(self):
           """Set up test fixtures."""
           self.mock_teps_manager = MagicMock()
           self.handler = ToolRequestHandler(self.mock_teps_manager)
           
           # Sample tool request
           self.sample_request = {
               "request_id": "req123",
               "tool_name": "test_tool",
               "parameters": {
                   "param1": "value1",
                   "param2": "value2"
               }
           }
           
           # Sample tool result
           self.sample_result = {
               "request_id": "req123",
               "tool_name": "test_tool",
               "status": "success",
               "data": {
                   "result": "Tool execution successful"
               }
           }
           
           # Configure mock to return the sample result
           self.mock_teps_manager.execute_tool.return_value = self.sample_result
           
       def test_process_tool_request_success(self):
           """Test processing a tool request successfully."""
           result = self.handler.process_tool_request(self.sample_request)
           
           # Verify TEPS manager was called with correct request
           self.mock_teps_manager.execute_tool.assert_called_once_with(self.sample_request)
           
           # Verify result is passed through
           self.assertEqual(result, self.sample_result)
           
       def test_process_tool_request_validation_error(self):
           """Test validation error for invalid tool request."""
           # Missing required field
           invalid_request = {
               "request_id": "req123",
               "tool_name": "test_tool"
               # Missing 'parameters'
           }
           
           with self.assertRaises(ValueError):
               self.handler.process_tool_request(invalid_request)
               
           # Invalid type for tool_name
           invalid_request = {
               "request_id": "req123",
               "tool_name": 123,  # Should be string
               "parameters": {}
           }
           
           with self.assertRaises(ValueError):
               self.handler.process_tool_request(invalid_request)
               
       def test_process_tool_request_execution_error(self):
           """Test handling of tool execution errors."""
           # Configure mock to raise an exception
           self.mock_teps_manager.execute_tool.side_effect = Exception("Tool execution failed")
           
           with self.assertRaises(ToolExecutionError):
               self.handler.process_tool_request(self.sample_request)
               
       def test_process_batch_tool_requests(self):
           """Test processing multiple tool requests in batch."""
           # Create a second request
           second_request = {
               "request_id": "req456",
               "tool_name": "other_tool",
               "parameters": {
                   "param1": "valueA"
               }
           }
           
           # Configure mock to return different results for each call
           second_result = {
               "request_id": "req456",
               "tool_name": "other_tool",
               "status": "success",
               "data": {
                   "result": "Second tool execution successful"
               }
           }
           
           self.mock_teps_manager.execute_tool.side_effect = [
               self.sample_result,
               second_result
           ]
           
           # Process batch
           results = self.handler.process_batch_tool_requests([self.sample_request, second_request])
           
           # Verify both requests were processed
           self.assertEqual(len(results), 2)
           self.assertEqual(results[0]["request_id"], "req123")
           self.assertEqual(results[1]["request_id"], "req456")
           
       def test_batch_continues_after_error(self):
           """Test that batch processing continues after an error."""
           # Configure mock to raise an exception on first call but succeed on second
           second_result = {
               "request_id": "req456",
               "tool_name": "other_tool",
               "status": "success",
               "data": {
                   "result": "Second tool execution successful"
               }
           }
           
           self.mock_teps_manager.execute_tool.side_effect = [
               Exception("First tool failed"),
               second_result
           ]
           
           # Create a second request
           second_request = {
               "request_id": "req456",
               "tool_name": "other_tool",
               "parameters": {
                   "param1": "valueA"
               }
           }
           
           # Process batch
           results = self.handler.process_batch_tool_requests([self.sample_request, second_request])
           
           # Verify both requests were processed
           self.assertEqual(len(results), 2)
           self.assertEqual(results[0]["status"], "error")  # First request failed
           self.assertEqual(results[1]["status"], "success")  # Second request succeeded
           
       def test_format_tool_result_as_message(self):
           """Test formatting a tool result as a message."""
           message = self.handler.format_tool_result_as_message(self.sample_result)
           
           # Verify message format
           self.assertEqual(message["role"], "tool_result")
           self.assertEqual(message["tool_name"], "test_tool")
           self.assertEqual(message["tool_call_id"], "req123")
           
           # Content should be serialized
           self.assertIsInstance(message["content"], str)
   ```

**Dependencies:** Phase 1 components, Message Manager

**Time Estimate:** 90 minutes

---

### Step 3: User Interface Manager Implementation

**Objective:** Implement the User Interface Manager component to handle user input and output formatting.

**Tasks:**

1. Create the ui_manager.py file with the UserInterfaceManager class:
   ```python
   """
   User interface management for the Framework Core Application.
   
   This module handles user input and output formatting.
   """
   
   import sys
   import os
   import re
   from typing import Callable, Optional, Dict, Any, List
   
   from framework_core.utils.logging_utils import setup_logger
   
   class UserInterfaceManager:
       """
       Manages user interface interactions, including input/output and formatting.
       """
       
       # ANSI color codes
       COLORS = {
           "reset": "\033[0m",
           "bold": "\033[1m",
           "red": "\033[31m",
           "green": "\033[32m",
           "yellow": "\033[33m",
           "blue": "\033[34m",
           "magenta": "\033[35m",
           "cyan": "\033[36m",
           "white": "\033[37m",
           "gray": "\033[90m"
       }
       
       def __init__(
           self, 
           config: Optional[Dict[str, Any]] = None,
           input_handler: Optional[Callable[[str], str]] = None,
           output_handler: Optional[Callable[[str], None]] = None
       ):
           """
           Initialize the User Interface Manager.
           
           Args:
               config: Optional configuration dictionary
               input_handler: Optional custom input handler function
               output_handler: Optional custom output handler function
           """
           self.logger = setup_logger("ui_manager")
           self.config = config or {}
           self.input_handler = input_handler or self._default_input_handler
           self.output_handler = output_handler or self._default_output_handler
           
           # Configure from config dict
           self.input_prompt = self.config.get("input_prompt", "> ")
           self.assistant_prefix = self.config.get("assistant_prefix", "(AI): ")
           self.system_prefix = self.config.get("system_prefix", "[System]: ")
           self.error_prefix = self.config.get("error_prefix", "[Error]: ")
           
           # Check if color is supported and enabled
           self.use_color = self.config.get("use_color", self._supports_color())
           
       def display_assistant_message(self, message: str) -> None:
           """
           Display an assistant message to the user.
           
           Args:
               message: The message to display
           """
           formatted_message = self._format_assistant_message(message)
           self.output_handler(formatted_message)
           
       def display_system_message(self, message: str) -> None:
           """
           Display a system message to the user.
           
           Args:
               message: The message to display
           """
           formatted_message = self._format_system_message(message)
           self.output_handler(formatted_message)
           
       def display_error_message(self, error_type: str, error_message: str) -> None:
           """
           Display an error message to the user.
           
           Args:
               error_type: The type of error
               error_message: The error message
           """
           formatted_message = self._format_error_message(error_type, error_message)
           self.output_handler(formatted_message)
           
       def get_user_input(self, prompt: Optional[str] = None) -> str:
           """
           Get input from the user.
           
           Args:
               prompt: Optional custom prompt
               
           Returns:
               User input string
           """
           prompt = prompt or self.input_prompt
           return self.input_handler(prompt)
           
       def get_multiline_input(
           self, 
           prompt: Optional[str] = None, 
           end_marker: str = ""
       ) -> str:
           """
           Get multi-line input from the user.
           
           Args:
               prompt: Optional custom prompt
               end_marker: String that marks the end of input
               
           Returns:
               Multi-line user input
           """
           prompt = prompt or "Enter multiple lines (submit empty line or '{end}' to finish):\n".format(
               end=end_marker or "<empty line>"
           )
           
           self.output_handler(prompt)
           
           lines = []
           while True:
               line = self.input_handler("")
               
               if (not line and not end_marker) or line == end_marker:
                   break
                   
               lines.append(line)
               
           return "\n".join(lines)
           
       def display_special_command_help(self, commands: Dict[str, str]) -> None:
           """
           Display help for special commands.
           
           Args:
               commands: Dictionary mapping command names to descriptions
           """
           if not commands:
               return
               
           help_message = "Available Commands:\n\n"
           
           max_len = max(len(cmd) for cmd in commands.keys())
           
           for cmd, desc in sorted(commands.items()):
               help_message += f"  {cmd.ljust(max_len)}  - {desc}\n"
               
           formatted_message = self._format_system_message(help_message)
           self.output_handler(formatted_message)
           
       def _format_assistant_message(self, message: str) -> str:
           """
           Format an assistant message for display.
           
           Args:
               message: The message to format
               
           Returns:
               Formatted message
           """
           if self.use_color:
               prefix = f"{self.COLORS['green']}{self.COLORS['bold']}{self.assistant_prefix}{self.COLORS['reset']}"
           else:
               prefix = self.assistant_prefix
               
           return f"{prefix}{message}"
           
       def _format_system_message(self, message: str) -> str:
           """
           Format a system message for display.
           
           Args:
               message: The message to format
               
           Returns:
               Formatted message
           """
           if self.use_color:
               prefix = f"{self.COLORS['blue']}{self.COLORS['bold']}{self.system_prefix}{self.COLORS['reset']}"
           else:
               prefix = self.system_prefix
               
           return f"{prefix}{message}"
           
       def _format_error_message(self, error_type: str, error_message: str) -> str:
           """
           Format an error message for display.
           
           Args:
               error_type: The type of error
               error_message: The error message
               
           Returns:
               Formatted message
           """
           if self.use_color:
               prefix = f"{self.COLORS['red']}{self.COLORS['bold']}{self.error_prefix}{self.COLORS['reset']}"
               error_type_str = f"{self.COLORS['red']}{self.COLORS['bold']}{error_type}{self.COLORS['reset']}"
           else:
               prefix = self.error_prefix
               error_type_str = error_type
               
           return f"{prefix}{error_type_str}: {error_message}"
           
       def _default_input_handler(self, prompt: str) -> str:
           """
           Default input handler implementation.
           
           Args:
               prompt: Input prompt
               
           Returns:
               User input
           """
           try:
               return input(prompt)
           except EOFError:
               # Handle Ctrl+D gracefully
               print()  # Add newline
               return ""
           except KeyboardInterrupt:
               # Handle Ctrl+C by returning empty string
               print()  # Add newline
               return ""
           
       def _default_output_handler(self, message: str) -> None:
           """
           Default output handler implementation.
           
           Args:
               message: Message to output
           """
           print(message)
           
       def _supports_color(self) -> bool:
           """
           Check if the terminal supports color output.
           
           Returns:
               True if color is supported, False otherwise
           """
           # Check if NO_COLOR environment variable is set
           if os.environ.get("NO_COLOR") is not None:
               return False
               
           # Check if output is a TTY
           if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
               return False
               
           # Check platform-specific color support
           platform = sys.platform.lower()
           if platform == "win32":
               # On Windows, check for ANSICON or ConEMU or Windows Terminal
               return (
                   "ANSICON" in os.environ
                   or "WT_SESSION" in os.environ
                   or "ConEmuANSI" in os.environ
                   or os.environ.get("TERM_PROGRAM") == "vscode"
               )
           else:
               # On Unix-like platforms, check TERM environment variable
               return os.environ.get("TERM") not in (None, "", "dumb")
   ```

2. Implement unit tests for the UserInterfaceManager class:
   ```python
   """
   Unit tests for the User Interface Manager.
   """
   
   import unittest
   from unittest.mock import patch, MagicMock
   import io
   import sys
   
   from framework_core.ui_manager import UserInterfaceManager
   
   class TestUserInterfaceManager(unittest.TestCase):
       """Test cases for UserInterfaceManager."""
       
       def setUp(self):
           """Set up test fixtures."""
           self.config = {
               "input_prompt": "$ ",
               "assistant_prefix": "[Bot]: ",
               "system_prefix": "[Sys]: ",
               "error_prefix": "[Err]: ",
               "use_color": False
           }
           
           # Create manager with mock handlers
           self.input_mock = MagicMock(return_value="mock user input")
           self.output_mock = MagicMock()
           
           self.manager = UserInterfaceManager(
               config=self.config,
               input_handler=self.input_mock,
               output_handler=self.output_mock
           )
           
       def test_display_assistant_message(self):
           """Test displaying assistant messages."""
           self.manager.display_assistant_message("Hello, user")
           
           # Check output_handler was called with formatted message
           self.output_mock.assert_called_once()
           arg = self.output_mock.call_args[0][0]
           self.assertTrue(arg.startswith("[Bot]: "))
           self.assertTrue("Hello, user" in arg)
           
       def test_display_system_message(self):
           """Test displaying system messages."""
           self.manager.display_system_message("System notification")
           
           # Check output_handler was called with formatted message
           self.output_mock.assert_called_once()
           arg = self.output_mock.call_args[0][0]
           self.assertTrue(arg.startswith("[Sys]: "))
           self.assertTrue("System notification" in arg)
           
       def test_display_error_message(self):
           """Test displaying error messages."""
           self.manager.display_error_message("ValidationError", "Invalid input")
           
           # Check output_handler was called with formatted message
           self.output_mock.assert_called_once()
           arg = self.output_mock.call_args[0][0]
           self.assertTrue(arg.startswith("[Err]: "))
           self.assertTrue("ValidationError" in arg)
           self.assertTrue("Invalid input" in arg)
           
       def test_get_user_input(self):
           """Test getting user input."""
           result = self.manager.get_user_input()
           
           # Check input_handler was called with configured prompt
           self.input_mock.assert_called_once_with("$ ")
           
           # Check result is returned from input_handler
           self.assertEqual(result, "mock user input")
           
           # Test with custom prompt
           self.input_mock.reset_mock()
           result = self.manager.get_user_input("Custom: ")
           self.input_mock.assert_called_once_with("Custom: ")
           
       def test_get_multiline_input(self):
           """Test getting multi-line input."""
           # Mock input to return three lines then end marker
           self.input_mock.side_effect = ["Line 1", "Line 2", "Line 3", "END"]
           
           result = self.manager.get_multiline_input(end_marker="END")
           
           # Check result contains all lines
           self.assertEqual(result, "Line 1\nLine 2\nLine 3")
           
           # Check input_handler was called four times
           self.assertEqual(self.input_mock.call_count, 4)
           
       def test_display_special_command_help(self):
           """Test displaying special command help."""
           commands = {
               "/help": "Show this help message",
               "/quit": "Exit the application",
               "/clear": "Clear conversation history"
           }
           
           self.manager.display_special_command_help(commands)
           
           # Check output_handler was called with formatted help
           self.output_mock.assert_called_once()
           arg = self.output_mock.call_args[0][0]
           
           # Check all commands are in the output
           for cmd in commands.keys():
               self.assertTrue(cmd in arg)
               
           # Check all descriptions are in the output
           for desc in commands.values():
               self.assertTrue(desc in arg)
               
       @patch('sys.stdout', new_callable=io.StringIO)
       def test_default_output_handler(self, mock_stdout):
           """Test the default output handler."""
           # Create manager with default handlers
           manager = UserInterfaceManager(config=self.config)
           
           # Call internal method directly
           manager._default_output_handler("Test message")
           
           # Check output was written to stdout
           self.assertEqual(mock_stdout.getvalue().strip(), "Test message")
           
       @patch('builtins.input', return_value="User input")
       def test_default_input_handler(self, mock_input):
           """Test the default input handler."""
           # Create manager with default handlers
           manager = UserInterfaceManager(config=self.config)
           
           # Call internal method directly
           result = manager._default_input_handler("Prompt: ")
           
           # Check input was called with prompt
           mock_input.assert_called_once_with("Prompt: ")
           
           # Check result is returned from input
           self.assertEqual(result, "User input")
   ```

**Dependencies:** Phase 1 components

**Time Estimate:** 90 minutes

---

### Step 4: Update Framework Controller with Main Interaction Loop

**Objective:** Update the Framework Controller to implement the main interaction loop.

**Tasks:**

1. Update the controller.py file with the main interaction loop:
   ```python
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
               self.tool_request_handler = ToolRequestHandler(
                   teps_manager=self.teps_manager
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
               self.dcm_manager.initialize()
               
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
               llm_settings = self.config_manager.get_llm_settings()
               
               self.logger.info(f"Initializing LIAL with provider: {llm_provider}")
               
               self.lial_manager = LIALManager(
                   llm_provider=llm_provider,
                   llm_settings=llm_settings,
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
               initial_prompt = self.dcm_manager.get_initial_prompt()
               if initial_prompt:
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
               error_msg = "Cannot run: components not initialized"
               self.logger.error(error_msg)
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
                   if "conversation" in llm_response:
                       assistant_message = llm_response["conversation"]
                       self.message_manager.add_assistant_message(assistant_message)
                       self.ui_manager.display_assistant_message(assistant_message)
                   
                   # Handle tool requests if present
                   if "tool_request" in llm_response and llm_response["tool_request"]:
                       self._handle_tool_request(llm_response["tool_request"])
                       
                       # Continue the conversation without user input
                       continue
                   
                   # Get user input
                   user_input = self.ui_manager.get_user_input()
                   
                   # Process special commands
                   if self._process_special_command(user_input):
                       continue
                   
                   # Add user message to history
                   self.message_manager.add_user_message(user_input)
                   
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
               llm_response = self.lial_manager.send_messages(messages)
               
               # Validate and sanitize response
               if not isinstance(llm_response, dict):
                   self.logger.warning("LLM response is not a dictionary")
                   llm_response = {
                       "conversation": "I encountered an issue processing your request. Please try again.",
                       "tool_request": None
                   }
                   
               return llm_response
               
           except Exception as e:
               self.logger.error(f"Error processing messages with LLM: {str(e)}")
               return {
                   "conversation": f"I encountered an error: {str(e)}",
                   "tool_request": None
               }
           
       def _handle_tool_request(self, tool_request: Dict[str, Any]) -> None:
           """
           Handle a tool request via the Tool Request Handler.
           
           Args:
               tool_request: The tool request to process
           """
           try:
               self.logger.info(f"Processing tool request: {tool_request.get('tool_name', 'unknown')}")
               
               # Process the tool request
               tool_result = self.tool_request_handler.process_tool_request(tool_request)
               
               # Format the result as a message
               tool_message = self.tool_request_handler.format_tool_result_as_message(tool_result)
               
               # Add the result to the message history
               self.message_manager.add_tool_result_message(
                   tool_name=tool_message["tool_name"],
                   content=tool_message["content"],
                   tool_call_id=tool_message["tool_call_id"]
               )
               
               if self.debug_mode:
                   # In debug mode, display tool result to user
                   debug_msg = f"Tool '{tool_message['tool_name']}' executed with result: {tool_message['content']}"
                   self.ui_manager.display_system_message(debug_msg)
                   
           except Exception as e:
               error_message = self.error_handler.handle_error(
                   "Tool Execution Error", 
                   str(e), 
                   exception=e
               )
               self.ui_manager.display_error_message("Tool Execution Error", error_message)
               
               # Add error message to conversation
               error_content = f"Error executing tool: {str(e)}"
               if isinstance(tool_request, dict) and "tool_name" in tool_request and "request_id" in tool_request:
                   self.message_manager.add_tool_result_message(
                       tool_name=tool_request["tool_name"],
                       content=error_content,
                       tool_call_id=tool_request["request_id"]
                   )
           
       def _process_special_command(self, user_input: str) -> bool:
           """
           Process special commands.
           
           Args:
               user_input: The user input string
               
           Returns:
               True if a special command was processed, False otherwise
           """
           # Ignore empty input
           if not user_input:
               return False
               
           # Check for special commands
           if user_input.startswith("/"):
               command = user_input.split(" ")[0].lower()
               
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
                   system_content = user_input[len("/system "):].strip()
                   if system_content:
                       self.message_manager.add_system_message(system_content)
                       self.ui_manager.display_system_message(f"Added system message: {system_content}")
                   else:
                       self.ui_manager.display_error_message("Command Error", "System message cannot be empty")
                   return True
                   
               elif command == "/debug":
                   self.debug_mode = not self.debug_mode
                   status = "enabled" if self.debug_mode else "disabled"
                   self.ui_manager.display_system_message(f"Debug mode {status}")
                   return True
           
           return False
           
       def shutdown(self) -> None:
           """
           Perform graceful shutdown of the framework.
           """
           self.logger.info("Framework shutdown initiated")
           self.running = False
           
           # Cleanup resources if needed
           # (components will be garbage collected)
           
           self.logger.info("Framework shutdown complete")
   ```

2. Update the run_framework.py file to use the new components:
   ```python
   #!/usr/bin/env python3
   """
   Main entry point for the Framework Core Application.
   
   This script initializes the framework components and starts the application.
   """
   
   import os
   import sys
   import argparse
   from typing import Dict, Any
   
   # Add parent directory to path if needed
   sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
   
   from framework_core.config_loader import ConfigurationManager
   from framework_core.controller import FrameworkController
   from framework_core.utils.logging_utils import setup_logger
   from framework_core.exceptions import ConfigError, ComponentInitError
   
   def parse_arguments() -> tuple:
       """
       Parse command-line arguments.
       
       Returns:
           Tuple of (config_path, args_dict)
       """
       parser = argparse.ArgumentParser(description="Framework Core Application")
       
       parser.add_argument(
           "--config", 
           "-c", 
           dest="config_path",
           help="Path to configuration file"
       )
       
       parser.add_argument(
           "--log-level", 
           "-l", 
           dest="logging.level",
           choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
           help="Logging level"
       )
       
       parser.add_argument(
           "--llm-provider", 
           dest="llm_provider",
           help="LLM provider to use"
       )
       
       parser.add_argument(
           "--context-file", 
           dest="context_definition_file",
           help="Path to context definition file"
       )
       
       # Parse args and convert to dict
       args = parser.parse_args()
       config_path = args.config_path
       
       # Remove config_path and convert the rest to a dict
       args_dict = {k: v for k, v in vars(args).items() if k != "config_path" and v is not None}
       
       return config_path, args_dict
   
   def main() -> int:
       """
       Main entry point function.
       
       Returns:
           Exit code (0 for success, non-zero for failure)
       """
       logger = setup_logger("main")
       logger.info("Starting Framework Core Application")
       
       try:
           # Parse command-line arguments
           config_path, cmd_args = parse_arguments()
           
           # Initialize configuration
           config_manager = ConfigurationManager(config_path, cmd_args)
           if not config_manager.load_configuration():
               logger.error("Failed to load configuration")
               return 1
               
           # Initialize framework controller
           controller = FrameworkController(config_manager)
           if not controller.initialize():
               logger.error("Failed to initialize framework controller")
               return 1
               
           # Run the application
           controller.run()
           
           return 0
           
       except ConfigError as e:
           logger.error(f"Configuration error: {str(e)}")
           print(f"Configuration error: {str(e)}")
           return 1
           
       except ComponentInitError as e:
           logger.error(f"Component initialization error: {str(e)}")
           print(f"Component initialization error: {str(e)}")
           return 1
           
       except KeyboardInterrupt:
           logger.info("Framework terminated by user")
           print("\nFramework terminated by user")
           return 0
           
       except Exception as e:
           logger.exception(f"Unhandled exception: {str(e)}")
           print(f"Unhandled exception: {str(e)}")
           return 1
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

3. Implement integration tests for the main loop:
   ```python
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
   ```

**Dependencies:** Phase 1 components, Message Manager, Tool Request Handler, UI Manager

**Time Estimate:** 120 minutes

---

### Step 5: Configuration and Sample Files

**Objective:** Create configuration files and sample context definitions.

**Tasks:**

1. Create a default configuration file (config/config.yaml):
   ```yaml
   # Basic Settings
   llm_provider: "gemini_2_5_pro"  # Identifies which LIAL adapter to use
   api_key_env_var: "GEMINI_API_KEY"  # Environment variable name for the API key
   context_definition_file: "./config/FRAMEWORK_CONTEXT.md"  # Path to context definition
   
   # LLM Provider Specific Settings
   llm_settings:
     gemini_2_5_pro:
       model_name: "gemini-1.5-pro-latest"
       temperature: 0.7
       max_output_tokens: 8192
       top_k: 40
       top_p: 0.95
       system_instruction_id: "system_prompt"  # Optional ID of system instruction in context
   
   # TEPS Settings
   teps_settings:
     allowlist_file: ".project_teps_allowlist.json"
     default_confirmation: false
     remember_confirmations: true
   
   # Logging Configuration
   logging:
     level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
     format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
     file: "framework.log"  # Set to null for console only
   
   # Message History Settings
   message_history:
     max_length: 100
     prioritize_system_messages: true
     pruning_strategy: "remove_oldest"  # remove_oldest, summarize
   
   # User Interface Settings
   ui:
     input_prompt: "> "
     assistant_prefix: "(AI): "
     system_prefix: "[System]: "
     error_prefix: "[Error]: "
     use_color: true
   ```

2. Create a sample context definition file (FRAMEWORK_CONTEXT.md.example):
   ```markdown
   # Framework Context Definition
   
   # initial_prompt_template: "Welcome to the AI-Assisted Framework. I'm here to help you with your task. How can I assist you today?"
   
   ## Personas
   catalyst_persona: @personas/catalyst_persona.md
   forge_persona: @personas/forge_persona.md
   
   ## Standards
   ai_dev_bible: @standards/ai_assisted_dev_bible.md
   
   ## Workflows
   maia_workflow: @workflows/maia_workflow.md
   
   ## System Instructions
   system_prompt: @system/main_prompt.md
   ```

**Dependencies:** None

**Time Estimate:** 30 minutes

---

### Step 6: Update Documentation

**Objective:** Update documentation to reflect Phase 2 components and functionality.

**Tasks:**

1. Update the README.md file:
   ```markdown
   # Framework Core Application
   
   The Framework Core Application is the central orchestrator for the AI-Assisted Framework V2, integrating the LIAL (LLM Interaction Abstraction Layer), TEPS (Tool Execution & Permission Service), and DCM (Dynamic Context Manager) components.
   
   ## Current Status
   
   - ✅ Phase 1: Core Structure and Initialization Components
     - Project structure setup
     - Configuration management
     - Error handling
     - Component integration interfaces
     - Basic framework controller (initialization only)
     - Unit testing
     
   - ✅ Phase 2: Functional Components
     - Message Manager implementation
     - Tool Request Handler implementation
     - User Interface Manager implementation
     - Main interaction loop implementation
     - Integration testing
     
   - 🔄 Phase 3: To be planned
   
   ## Usage
   
   ### Prerequisites
   
   - Python 3.9+
   - PyYAML
   - Access to the Gemini API (or other supported LLM)
   
   ### Configuration
   
   1. Copy `config/config.yaml.example` to `config/config.yaml`
   2. Copy `config/FRAMEWORK_CONTEXT.md.example` to `config/FRAMEWORK_CONTEXT.md`
   3. Set up environment variables:
      ```bash
      export GEMINI_API_KEY="your-api-key"
      ```
   
   ### Running the Framework
   
   ```bash
   # Basic usage
   python run_framework.py
   
   # With custom config
   python run_framework.py --config /path/to/config.yaml
   
   # With command-line overrides
   python run_framework.py --log-level DEBUG --llm-provider gemini_2_5_pro
   ```
   
   ## Special Commands
   
   While using the application, you can use these special commands:
   
   - `/help` - Show this help message
   - `/quit` or `/exit` - Exit the application
   - `/clear` - Clear conversation history (preserves system messages)
   - `/system <message>` - Add a system message
   - `/debug` - Toggle debug mode
   
   ## Component Architecture
   
   The Framework Core Application consists of the following main components:
   
   1. **Framework Controller**: The central orchestrator that manages the interaction flow and component lifecycle.
   2. **Configuration Manager**: Handles loading, validation, and access to configuration settings.
   3. **Message Manager**: Maintains and manages conversation history.
   4. **Tool Request Handler**: Processes tool requests and manages execution via TEPS.
   5. **User Interface Manager**: Handles user input and output formatting.
   6. **Component Managers**: Abstract interfaces for interacting with LIAL, TEPS, and DCM.
   7. **Error Handler**: Centralized error handling and logging.
   
   ## Development
   
   ### Running Tests
   
   ```bash
   # Run all tests
   python -m unittest discover
   
   # Run specific test file
   python -m unittest tests/unit/test_message_manager.py
   ```
   
   ### Adding New LLM Providers
   
   To add support for a new LLM provider:
   
   1. Create a new adapter class in `framework_core/adapters/`
   2. Implement the required interface methods
   3. Register the adapter in the LIALManager's `_get_adapter_class` method
   4. Add provider-specific configuration options to the config schema
   ```

**Dependencies:** All previous steps

**Time Estimate:** 30 minutes

---

### Step 7: Comprehensive Testing

**Objective:** Test the integrated application with all Phase 2 components.

**Tasks:**

1. Write comprehensive integration tests for the complete application.
2. Perform manual testing of the main interaction loop.
3. Ensure all components work together correctly.
4. Verify error handling for various edge cases.

**Dependencies:** All previous implementation steps

**Time Estimate:** 90 minutes

## 3. Timeline

Based on the implementation steps outlined above, here's an estimated timeline for Phase 2 implementation:

1. Message Manager Implementation: 90 minutes
2. Tool Request Handler Implementation: 90 minutes
3. User Interface Manager Implementation: 90 minutes
4. Update Framework Controller with Main Interaction Loop: 120 minutes
5. Configuration and Sample Files: 30 minutes
6. Update Documentation: 30 minutes
7. Comprehensive Testing: 90 minutes

**Total Estimated Time:** 540 minutes (approximately 9 hours)

This estimate assumes that the developer is familiar with Python and has already completed Phase 1. Actual implementation time may vary based on experience level and unforeseen technical challenges.

## 4. Testing Strategy

1. **Unit Testing:**
   - Each new component (MessageManager, ToolRequestHandler, UserInterfaceManager) should have its own test suite
   - Test individual methods and functionality in isolation
   - Mock dependencies to isolate component behavior
   - Focus on testing edge cases and error handling
   - Aim for >85% code coverage

2. **Integration Testing:**
   - Test the interaction between components
   - Test the main loop with mocked LLM responses
   - Test tool request handling flow
   - Test message history management during interaction

3. **System Testing:**
   - Test the complete application end-to-end
   - Test with realistic configuration
   - Test special commands
   - Test error recovery and graceful degradation

4. **Manual Testing:**
   - Test user interface formatting
   - Test multi-line input
   - Test with long conversations to verify pruning
   - Test tool request execution with TEPS

## 5. Conclusion

This implementation plan provides a comprehensive guide for implementing Phase 2 of the Framework Core Application. By following the steps outlined above, Forge should be able to create the remaining components needed for a functional application that can process user input, interact with the LLM via LIAL, execute tools via TEPS, and maintain conversation history.

The implementation focuses on creating a robust, maintainable, and extensible application with clear separation of concerns, comprehensive error handling, and thorough testing. The components are designed to be modular and reusable, allowing for future extensions and enhancements.

Upon completion of Phase 2, the Framework Core Application will be a fully functional application capable of handling user interactions, processing LLM responses, executing tools, and maintaining conversation history.