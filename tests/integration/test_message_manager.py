"""
Integration tests for the MessageManager component.

These tests verify the MessageManager's handling of message history,
including adding, retrieving, and managing different message types.
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.message_manager import MessageManager
from framework_core.lial_core import Message
from tests.integration.utils import IntegrationTestCase


class TestMessageManagerIntegration(IntegrationTestCase):
    """
    Integration tests for the MessageManager component.
    
    These tests validate that:
    1. Different message types are handled correctly
    2. Message history is maintained properly
    3. Pruning logic works as expected
    4. Message formatting for LLM interactions is correct
    5. The MessageManager properly integrates with other components
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        super().setup_method()
        
        # Create a standard config for MessageManager
        self.standard_config = {
            "max_length": 100,
            "pruning_strategy": "remove_oldest",
            "prioritize_system_messages": True
        }
        
        # Create a MessageManager instance
        self.message_manager = MessageManager(config=self.standard_config)
        
        # Set up some standard messages for testing
        self.system_message = "You are an AI assistant in the KeystoneAI Framework."
        self.user_message = "Hello, who are you?"
        self.assistant_message = "I am an AI assistant. How can I help you today?"
        self.tool_result_message = "Content of the requested file."
        self.tool_name = "readFile"
        self.tool_call_id = "read-123"
    
    def test_add_different_message_types(self):
        """Test adding different types of messages to the message history."""
        # Add system message
        self.message_manager.add_system_message(self.system_message)
        
        # Add user message
        self.message_manager.add_user_message(self.user_message)
        
        # Add assistant message
        self.message_manager.add_assistant_message(self.assistant_message)
        
        # Add tool result message
        self.message_manager.add_tool_result_message(
            tool_name=self.tool_name,
            content=self.tool_result_message,
            tool_call_id=self.tool_call_id
        )
        
        # Get all messages
        all_messages = self.message_manager.get_messages()
        
        # Verify message count
        assert len(all_messages) == 4
        
        # Verify message types and order
        assert all_messages[0]["role"] == "system"
        assert all_messages[0]["content"] == self.system_message
        
        assert all_messages[1]["role"] == "user"
        assert all_messages[1]["content"] == self.user_message
        
        assert all_messages[2]["role"] == "assistant"
        assert all_messages[2]["content"] == self.assistant_message
        
        assert all_messages[3]["role"] == "tool_result"
        assert all_messages[3]["content"] == self.tool_result_message
        assert all_messages[3]["tool_name"] == self.tool_name
        assert all_messages[3]["tool_call_id"] == self.tool_call_id
    
    def test_get_messages_filtering(self):
        """Test filtering messages by role when retrieving them."""
        # Add messages of different types
        self.message_manager.add_system_message(self.system_message)
        self.message_manager.add_user_message(self.user_message)
        self.message_manager.add_assistant_message(self.assistant_message)
        self.message_manager.add_tool_result_message(
            tool_name=self.tool_name,
            content=self.tool_result_message,
            tool_call_id=self.tool_call_id
        )
        
        # Get only system messages
        system_messages = self.message_manager.get_messages(include_roles=["system"])
        assert len(system_messages) == 1
        assert system_messages[0]["role"] == "system"
        
        # Get user and assistant messages
        user_assistant_messages = self.message_manager.get_messages(
            include_roles=["user", "assistant"]
        )
        assert len(user_assistant_messages) == 2
        assert user_assistant_messages[0]["role"] == "user"
        assert user_assistant_messages[1]["role"] == "assistant"
        
        # Exclude tool_result messages
        non_tool_messages = self.message_manager.get_messages(
            exclude_roles=["tool_result"]
        )
        assert len(non_tool_messages) == 3
        assert all(msg["role"] != "tool_result" for msg in non_tool_messages)
    
    def test_format_messages_for_llm(self):
        """Test formatting messages for LLM consumption."""
        # Add messages of different types
        self.message_manager.add_system_message(self.system_message)
        self.message_manager.add_user_message(self.user_message)
        self.message_manager.add_assistant_message(self.assistant_message)
        self.message_manager.add_tool_result_message(
            tool_name=self.tool_name,
            content=self.tool_result_message,
            tool_call_id=self.tool_call_id
        )
        
        # Get messages formatted for LLM
        llm_messages = self.message_manager.get_messages(for_llm=True)
        
        # Verify count
        assert len(llm_messages) == 4
        
        # Verify tool_result is transformed to "tool" role for LLM
        assert llm_messages[3]["role"] == "tool"
        assert llm_messages[3]["name"] == self.tool_name
        assert llm_messages[3]["content"] == self.tool_result_message
        assert llm_messages[3]["tool_call_id"] == self.tool_call_id
        
        # Verify other messages are unchanged
        assert llm_messages[0]["role"] == "system"
        assert llm_messages[1]["role"] == "user"
        assert llm_messages[2]["role"] == "assistant"
    
    def test_clear_history(self):
        """Test clearing message history with and without preserving system messages."""
        # Add messages of different types
        self.message_manager.add_system_message(self.system_message)
        self.message_manager.add_user_message(self.user_message)
        self.message_manager.add_assistant_message(self.assistant_message)
        
        # Clear history but preserve system messages
        self.message_manager.clear_history(preserve_system=True)
        
        # Verify only system message remains
        messages = self.message_manager.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "system"
        
        # Add more messages
        self.message_manager.add_user_message(self.user_message)
        self.message_manager.add_assistant_message(self.assistant_message)
        
        # Clear all history including system messages
        self.message_manager.clear_history(preserve_system=False)
        
        # Verify all messages are cleared
        messages = self.message_manager.get_messages()
        assert len(messages) == 0
    
    def test_message_pruning(self):
        """Test manual message pruning functionality."""
        # Test with a simpler case to isolate pruning behavior
        simple_manager = MessageManager(config={
            "max_length": 2,  # Very small limit for clear testing
            "pruning_strategy": "remove_oldest",
            "prioritize_system_messages": False  # Don't prioritize for this test
        })
        
        # Add three messages (exceeding the limit)
        simple_manager.add_user_message("First message")
        simple_manager.add_user_message("Second message")
        simple_manager.add_user_message("Third message")
        
        # Check initial count
        initial_messages = simple_manager.get_messages()
        initial_count = len(initial_messages)
        print(f"Initial message count: {initial_count}")
        for msg in initial_messages:
            print(f"Message: {msg['content']}")
        
        # Manually trigger pruning
        simple_manager.prune_history()
        
        # Check result
        pruned_messages = simple_manager.get_messages()
        pruned_count = len(pruned_messages)
        print(f"After pruning, message count: {pruned_count}")
        for msg in pruned_messages:
            print(f"Message after pruning: {msg['content']}")
        
        # Most basic assertion - length should be at most max_length
        assert pruned_count <= 2
        
        # The remaining messages should be the most recent ones
        message_contents = [msg["content"] for msg in pruned_messages]
        assert "Third message" in message_contents
        assert "First message" not in message_contents
    
    def test_prioritize_system_messages(self):
        """Test that system messages are preserved when prioritized."""
        # Create a MessageManager with small max_length to test system message priority
        system_priority_manager = MessageManager(config={
            "max_length": 3,  # Only keep 3 messages total
            "pruning_strategy": "remove_oldest",
            "prioritize_system_messages": True  # Prioritize system messages
        })
        
        # Add multiple system messages
        system_priority_manager.add_system_message("System message 1")
        system_priority_manager.add_system_message("System message 2")
        
        # Add user and assistant messages (total now exceeds max_length)
        system_priority_manager.add_user_message("User message")
        system_priority_manager.add_assistant_message("Assistant message")
        
        # Trigger pruning explicitly
        system_priority_manager.prune_history()
        
        # Get messages after pruning
        messages = system_priority_manager.get_messages()
        
        # Verify total count respects max_length
        assert len(messages) <= 3
        
        # When prioritizing system messages, all system messages should be preserved
        system_messages = [m for m in messages if m["role"] == "system"]
        assert len(system_messages) == 2, "System messages should be preserved when prioritized"
        
        # Compare with non-prioritizing behavior
        non_priority_manager = MessageManager(config={
            "max_length": 3,
            "pruning_strategy": "remove_oldest",
            "prioritize_system_messages": False  # Don't prioritize system messages
        })
        
        # Add the same sequence of messages
        non_priority_manager.add_system_message("System message 1")  # Oldest
        non_priority_manager.add_system_message("System message 2")  
        non_priority_manager.add_user_message("User message")
        non_priority_manager.add_assistant_message("Assistant message")  # Newest
        
        # Get messages before pruning
        pre_messages = non_priority_manager.get_messages()
        pre_count = len(pre_messages)
        print(f"Before pruning (no priority): {pre_count} messages")
        
        # Explicitly trigger pruning
        non_priority_manager.prune_history()
        
        # Get messages after pruning
        post_messages = non_priority_manager.get_messages()
        print(f"After pruning (no priority): {len(post_messages)} messages")
        
        # Verify count
        assert len(post_messages) <= 3
        
        # With no priority, the newest messages should be kept regardless of role
        message_contents = [m["content"] for m in post_messages]
        assert "Assistant message" in message_contents, "Newest message should be preserved"
    
    def test_conversation_flow(self):
        """Test a full conversation flow through the MessageManager."""
        # Start with system message
        self.message_manager.add_system_message(self.system_message)
        
        # First user question
        self.message_manager.add_user_message("What can you help me with?")
        
        # Assistant response
        self.message_manager.add_assistant_message("I can help you with a variety of tasks. Would you like me to read a file?")
        
        # User requests file reading
        self.message_manager.add_user_message("Yes, please read /path/to/file.txt")
        
        # Assistant acknowledges
        self.message_manager.add_assistant_message("I'll read that file for you.")
        
        # Tool result comes back
        self.message_manager.add_tool_result_message(
            tool_name="readFile",
            content="This is the content of the requested file.",
            tool_call_id="read-456"
        )
        
        # Assistant responds to tool result
        self.message_manager.add_assistant_message("I've read the file. It contains: 'This is the content of the requested file.'")
        
        # User asks a follow-up
        self.message_manager.add_user_message("Thank you. Can you summarize it?")
        
        # Get LLM-formatted messages
        llm_messages = self.message_manager.get_messages(for_llm=True)
        
        # Verify full conversation flow
        assert len(llm_messages) == 8
        
        # Verify conversation order
        roles = [msg["role"] for msg in llm_messages]
        expected_roles = ["system", "user", "assistant", "user", "assistant", "tool", "assistant", "user"]
        assert roles == expected_roles
        
        # Verify tool information is properly formatted
        tool_message = next(msg for msg in llm_messages if msg["role"] == "tool")
        assert tool_message["name"] == "readFile"
        assert "content of the requested file" in tool_message["content"]
    
    def test_message_count_tracking(self):
        """Test that message counts are tracked correctly."""
        # Add various message types
        self.message_manager.add_system_message("System message 1")
        self.message_manager.add_user_message("User message 1")
        self.message_manager.add_assistant_message("Assistant message 1")
        self.message_manager.add_tool_result_message(
            tool_name="readFile",
            content="Tool result 1",
            tool_call_id="tool-1"
        )
        
        # Get message counts
        messages = self.message_manager.get_messages()
        system_count = len([m for m in messages if m["role"] == "system"])
        user_count = len([m for m in messages if m["role"] == "user"])
        assistant_count = len([m for m in messages if m["role"] == "assistant"])
        tool_count = len([m for m in messages if m["role"] == "tool_result"])
        
        # Verify counts
        assert system_count == 1
        assert user_count == 1
        assert assistant_count == 1
        assert tool_count == 1
        
        # Add more messages
        self.message_manager.add_system_message("System message 2")
        self.message_manager.add_user_message("User message 2")
        self.message_manager.add_assistant_message("Assistant message 2")
        
        # Get updated counts
        messages = self.message_manager.get_messages()
        system_count = len([m for m in messages if m["role"] == "system"])
        user_count = len([m for m in messages if m["role"] == "user"])
        assistant_count = len([m for m in messages if m["role"] == "assistant"])
        
        # Verify updated counts
        assert system_count == 2
        assert user_count == 2
        assert assistant_count == 2
    
    def test_empty_history_handling(self):
        """Test behavior with empty message history."""
        # No messages added yet
        
        # Get messages from empty history
        empty_messages = self.message_manager.get_messages()
        
        # Verify empty list is returned
        assert isinstance(empty_messages, list)
        assert len(empty_messages) == 0
        
        # Get LLM-formatted messages from empty history
        empty_llm_messages = self.message_manager.get_messages(for_llm=True)
        
        # Verify empty list is returned
        assert isinstance(empty_llm_messages, list)
        assert len(empty_llm_messages) == 0
        
        # Clear an already empty history
        self.message_manager.clear_history()
        
        # Verify still empty
        assert len(self.message_manager.get_messages()) == 0
    
    def test_large_message_handling(self):
        """Test handling of large messages in history."""
        # Create a large message
        large_message = "A" * 10000  # 10,000 character message
        
        # Add large message
        self.message_manager.add_user_message(large_message)
        
        # Verify message was stored correctly
        messages = self.message_manager.get_messages()
        assert len(messages) == 1
        assert messages[0]["content"] == large_message
        assert len(messages[0]["content"]) == 10000
        
        # Add several large messages
        for i in range(5):
            self.message_manager.add_assistant_message(f"Large response {i}: " + "B" * 5000)
        
        # Verify all messages stored
        messages = self.message_manager.get_messages()
        assert len(messages) == 6  # 1 user + 5 assistant
        
        # Verify content preserved
        for i, msg in enumerate(messages[1:]):
            assert msg["role"] == "assistant"
            assert f"Large response {i}: " in msg["content"]
            assert len(msg["content"]) > 5000