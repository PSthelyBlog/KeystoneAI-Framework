#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for the Message Manager component.

These tests verify that the Message Manager correctly integrates with LIAL
and properly handles different message types including tool results.

AI-GENERATED: [Forge] - Task:[RFI-COREAPP-INT-TEST-001]
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the google.generativeai module before importing components
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

from framework_core.message_manager import MessageManager
from framework_core.lial_core import LLMAdapterInterface, Message, LLMResponse, ToolRequest
from framework_core.tool_request_handler import ToolRequestHandler


class MockLLMAdapter(LLMAdapterInterface):
    """Mock LLM Adapter for testing Message Manager integration."""
    
    def __init__(self, config: dict, dcm_instance=None) -> None:
        """Initialize the mock adapter."""
        self.config = config
        self.dcm = dcm_instance
        self.message_sequence_history = []
        self.persona_used = None
        self.response_to_return = None
    
    def send_message_sequence(self, messages: list, active_persona_id: str = None) -> dict:
        """Mock sending a message sequence to the LLM."""
        self.message_sequence_history.append({
            'messages': messages.copy(),
            'persona_id': active_persona_id
        })
        self.persona_used = active_persona_id
        
        # Return predetermined response if set, otherwise generate a default
        if self.response_to_return:
            return self.response_to_return
        
        # Look for tool result messages
        tool_results = [m for m in messages if m.get("role") == "tool_result"]
        if tool_results:
            # If there are tool results, incorporate them into the response
            tool_result = tool_results[-1]  # Get the most recent one
            tool_name = tool_result.get("tool_name", "unknown tool")
            content = tool_result.get("content", "{}")
            try:
                if isinstance(content, str) and content.startswith("{"):
                    content_obj = json.loads(content)
                    if "result" in content_obj:
                        content_summary = content_obj["result"]
                    else:
                        content_summary = str(content_obj)
                else:
                    content_summary = content
            except:
                content_summary = str(content)
                
            return {
                "conversation": f"I processed the {tool_name} result: {content_summary}",
                "tool_request": None
            }
        
        # Default response based on user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            user_content = user_messages[-1].get("content", "")
            
            if "file" in user_content.lower():
                return {
                    "conversation": "I'll help you with that file.",
                    "tool_request": {
                        "request_id": "read123",
                        "tool_name": "readFile",
                        "parameters": {
                            "path": "/example/test.txt"
                        }
                    }
                }
        
        return {
            "conversation": "This is a default response.",
            "tool_request": None
        }
    
    def set_response(self, response: dict) -> None:
        """Set a predetermined response for the next call."""
        self.response_to_return = response


class MockTEPS:
    """Mock TEPS for testing tool request handling."""
    
    def execute_tool(self, tool_request: dict) -> dict:
        """Mock tool execution."""
        if tool_request["tool_name"] == "readFile":
            return {
                "request_id": tool_request["request_id"],
                "tool_name": tool_request["tool_name"],
                "status": "success",
                "data": {
                    "content": "This is the content of the file.",
                    "file_path": tool_request["parameters"]["path"]
                }
            }
        else:
            return {
                "request_id": tool_request["request_id"],
                "tool_name": tool_request["tool_name"],
                "status": "success",
                "data": {
                    "result": "Generic tool execution result"
                }
            }


class TestMessageManagerIntegration(unittest.TestCase):
    """Test cases for Message Manager integration with other components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create message manager
        self.message_manager = MessageManager({
            "max_length": 100,
            "pruning_strategy": "remove_oldest",
            "prioritize_system_messages": True
        })
        
        # Create mock LLM adapter
        self.mock_lial_adapter = MockLLMAdapter({})
        
        # Create mock TEPS
        self.mock_teps = MockTEPS()
        
        # Create tool request handler with mock TEPS
        self.tool_request_handler = ToolRequestHandler(self.mock_teps)
    
    def test_message_history_integration_with_lial(self):
        """Test integration of message history with LIAL."""
        # Add some messages to the history
        self.message_manager.add_system_message("You are an AI assistant.")
        self.message_manager.add_user_message("Hello, how are you?")
        self.message_manager.add_assistant_message("I'm doing well, how can I help?")
        
        # Get messages for LLM
        messages_for_llm = self.message_manager.get_messages(for_llm=True)
        
        # Verify message count and format
        self.assertEqual(len(messages_for_llm), 3)
        self.assertEqual(messages_for_llm[0]["role"], "system")
        self.assertEqual(messages_for_llm[1]["role"], "user")
        self.assertEqual(messages_for_llm[2]["role"], "assistant")
        
        # Send messages to LIAL
        response = self.mock_lial_adapter.send_message_sequence(messages_for_llm)
        
        # Verify LIAL received the messages
        self.assertEqual(len(self.mock_lial_adapter.message_sequence_history), 1)
        received_messages = self.mock_lial_adapter.message_sequence_history[0]["messages"]
        self.assertEqual(len(received_messages), 3)
        
        # Add the response back to the message history
        self.message_manager.add_assistant_message(response["conversation"])
        
        # Verify the message history now has 4 messages
        self.assertEqual(len(self.message_manager.messages), 4)
        self.assertEqual(self.message_manager.messages[3]["role"], "assistant")
        self.assertEqual(self.message_manager.messages[3]["content"], response["conversation"])
    
    def test_tool_result_message_handling(self):
        """Test that tool results are correctly added to the message history and processed by LIAL."""
        # Initialize conversation
        self.message_manager.add_system_message("You are an AI assistant.")
        self.message_manager.add_user_message("Can you read a file for me?")
        
        # Simulate LLM response with tool request
        self.mock_lial_adapter.set_response({
            "conversation": "I'll read that file for you.",
            "tool_request": {
                "request_id": "read123",
                "tool_name": "readFile",
                "parameters": {
                    "path": "/example/test.txt"
                }
            }
        })
        
        # Send initial messages to LIAL
        messages_for_llm = self.message_manager.get_messages(for_llm=True)
        response = self.mock_lial_adapter.send_message_sequence(messages_for_llm)
        
        # Add assistant response to history
        self.message_manager.add_assistant_message(response["conversation"])
        
        # Extract tool request
        tool_request = response["tool_request"]
        
        # Execute the tool request
        tool_result = self.mock_teps.execute_tool(tool_request)
        
        # Add tool result to message history
        self.message_manager.add_tool_result_message(
            tool_name=tool_result["tool_name"],
            content=tool_result["data"],
            tool_call_id=tool_result["request_id"]
        )
        
        # Verify tool result was added to history
        self.assertEqual(len(self.message_manager.messages), 4)
        last_message = self.message_manager.messages[3]
        self.assertEqual(last_message["role"], "tool_result")
        self.assertEqual(last_message["tool_name"], "readFile")
        
        # Get updated messages for LLM
        updated_messages = self.message_manager.get_messages(for_llm=True)
        
        # Verify the tool result is formatted correctly for LLM
        tool_message = updated_messages[3]
        self.assertEqual(tool_message["role"], "tool")
        self.assertEqual(tool_message["name"], "readFile")
        
        # Send updated messages to LIAL
        follow_up_response = self.mock_lial_adapter.send_message_sequence(updated_messages)
        
        # Verify LIAL processed the tool result
        self.assertEqual(len(self.mock_lial_adapter.message_sequence_history), 2)
        self.assertTrue("processed the readFile result" in follow_up_response["conversation"])
        
        # Add the follow-up response to the message history
        self.message_manager.add_assistant_message(follow_up_response["conversation"])
        
        # Verify the message history now has 5 messages
        self.assertEqual(len(self.message_manager.messages), 5)
    
    def test_message_pruning_with_lial(self):
        """Test that message pruning works correctly and LIAL receives the pruned messages."""
        # Set a lower max history length for testing
        self.message_manager.max_history_length = 5
        
        # Add system message that should be preserved
        self.message_manager.add_system_message("You are an AI assistant.")
        
        # Add more messages than the max length
        for i in range(10):
            self.message_manager.add_user_message(f"User message {i}")
            self.message_manager.add_assistant_message(f"Assistant response {i}")
        
        # Prune the history
        self.message_manager.prune_history()
        
        # Verify history was pruned but system message preserved
        self.assertLessEqual(len(self.message_manager.messages), 5)
        self.assertEqual(self.message_manager.messages[0]["role"], "system")
        
        # Get pruned messages for LLM
        pruned_messages = self.message_manager.get_messages(for_llm=True)
        
        # Send pruned messages to LIAL
        response = self.mock_lial_adapter.send_message_sequence(pruned_messages)
        
        # Verify LIAL received the pruned messages
        self.assertEqual(len(self.mock_lial_adapter.message_sequence_history), 1)
        received_messages = self.mock_lial_adapter.message_sequence_history[0]["messages"]
        self.assertLessEqual(len(received_messages), 5)
        self.assertEqual(received_messages[0]["role"], "system")
    
    def test_filtering_messages_for_lial(self):
        """Test filtering messages before sending to LIAL."""
        # Add various message types
        self.message_manager.add_system_message("You are an AI assistant.")
        self.message_manager.add_user_message("Hello")
        self.message_manager.add_assistant_message("Hi there")
        self.message_manager.add_tool_result_message(
            tool_name="testTool",
            content={"result": "Test result"},
            tool_call_id="test123"
        )
        
        # Test filtering out tool results
        filtered_messages = self.message_manager.get_messages(
            exclude_roles=["tool_result"],
            for_llm=True
        )
        
        # Verify filtering
        self.assertEqual(len(filtered_messages), 3)
        roles = [m["role"] for m in filtered_messages]
        self.assertNotIn("tool", roles)  # "tool_result" becomes "tool" for LLM
        
        # Test including only specific roles
        user_messages = self.message_manager.get_messages(
            include_roles=["user"],
            for_llm=True
        )
        
        # Verify filtering
        self.assertEqual(len(user_messages), 1)
        self.assertEqual(user_messages[0]["role"], "user")
        
        # Send filtered messages to LIAL
        response = self.mock_lial_adapter.send_message_sequence(user_messages)
        
        # Verify LIAL received only the filtered messages
        self.assertEqual(len(self.mock_lial_adapter.message_sequence_history), 1)
        received_messages = self.mock_lial_adapter.message_sequence_history[0]["messages"]
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0]["role"], "user")
    
    def test_complete_message_cycle_with_lial_and_tools(self):
        """Test a complete message cycle with LIAL and tool execution."""
        # Start a conversation
        self.message_manager.add_system_message("You are an AI assistant.")
        
        # First user message
        self.message_manager.add_user_message("Can you read a file for me?")
        
        # Round 1: Get initial response with tool request
        round1_messages = self.message_manager.get_messages(for_llm=True)
        round1_response = self.mock_lial_adapter.send_message_sequence(round1_messages)
        
        # Add assistant response
        self.message_manager.add_assistant_message(round1_response["conversation"])
        
        # Handle tool request
        tool_request = round1_response["tool_request"]
        self.assertIsNotNone(tool_request)
        
        # Execute tool
        tool_result = self.tool_request_handler.handle_tool_request(tool_request)
        
        # Add tool result to history
        self.message_manager.add_tool_result_message(
            tool_name=tool_result["tool_name"],
            content=tool_result["data"],
            tool_call_id=tool_result["request_id"]
        )
        
        # Round 2: Send messages with tool result to get follow-up response
        round2_messages = self.message_manager.get_messages(for_llm=True)
        
        # Check that tool result is properly formatted for LLM
        tool_message = next((m for m in round2_messages if m["role"] == "tool"), None)
        self.assertIsNotNone(tool_message)
        self.assertEqual(tool_message["name"], "readFile")
        
        # Get follow-up response
        round2_response = self.mock_lial_adapter.send_message_sequence(round2_messages)
        
        # Add assistant response
        self.message_manager.add_assistant_message(round2_response["conversation"])
        
        # Check the complete conversation flow
        final_messages = self.message_manager.get_messages()
        
        # Verify we have the expected message sequence:
        # 1. System prompt
        # 2. User request
        # 3. Assistant response with tool intent
        # 4. Tool result
        # 5. Assistant follow-up incorporating tool result
        self.assertEqual(len(final_messages), 5)
        self.assertEqual(final_messages[0]["role"], "system")
        self.assertEqual(final_messages[1]["role"], "user")
        self.assertEqual(final_messages[2]["role"], "assistant")
        self.assertEqual(final_messages[3]["role"], "tool_result")
        self.assertEqual(final_messages[4]["role"], "assistant")
        
        # Verify LIAL received the proper message sequences
        self.assertEqual(len(self.mock_lial_adapter.message_sequence_history), 2)


if __name__ == "__main__":
    unittest.main()