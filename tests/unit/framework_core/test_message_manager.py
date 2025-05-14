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

if __name__ == "__main__":
    unittest.main()