"""
Unit tests for the MessageManager class.

This module tests all the functionality of the MessageManager class
located in framework_core/message_manager.py.
"""

import pytest
import time
import json
from unittest.mock import patch, MagicMock, ANY
from copy import deepcopy

from framework_core.message_manager import MessageManager

class TestMessageManager:
    """Test suite for the MessageManager class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        manager = MessageManager()
        assert manager.messages == []
        assert manager.max_history_length == 100
        assert manager.pruning_strategy == "remove_oldest"
        assert manager.prioritize_system_messages is True
        
    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "max_length": 50,
            "pruning_strategy": "summarize",
            "prioritize_system_messages": False
        }
        manager = MessageManager(config)
        assert manager.messages == []
        assert manager.max_history_length == 50
        assert manager.pruning_strategy == "summarize"
        assert manager.prioritize_system_messages is False
    
    @patch('time.time')
    def test_add_system_message(self, mock_time):
        """Test adding a system message."""
        mock_time.return_value = 1234567890
        
        manager = MessageManager()
        manager.add_system_message("System prompt")
        
        assert len(manager.messages) == 1
        assert manager.messages[0] == {
            "role": "system",
            "content": "System prompt",
            "timestamp": 1234567890
        }
    
    @patch('time.time')
    def test_add_user_message(self, mock_time):
        """Test adding a user message."""
        mock_time.return_value = 1234567890
        
        manager = MessageManager()
        manager.add_user_message("User message")
        
        assert len(manager.messages) == 1
        assert manager.messages[0] == {
            "role": "user",
            "content": "User message",
            "timestamp": 1234567890
        }
    
    @patch('time.time')
    def test_add_assistant_message(self, mock_time):
        """Test adding an assistant message."""
        mock_time.return_value = 1234567890
        
        manager = MessageManager()
        manager.add_assistant_message("Assistant response")
        
        assert len(manager.messages) == 1
        assert manager.messages[0] == {
            "role": "assistant",
            "content": "Assistant response",
            "timestamp": 1234567890
        }
    
    @patch('time.time')
    def test_add_tool_result_message_with_string_content(self, mock_time):
        """Test adding a tool result message with string content."""
        mock_time.return_value = 1234567890
        
        manager = MessageManager()
        manager.add_tool_result_message(
            tool_name="search",
            content="Search results",
            tool_call_id="tool_123"
        )
        
        assert len(manager.messages) == 1
        assert manager.messages[0] == {
            "role": "tool_result",
            "content": "Search results",
            "tool_name": "search",
            "tool_call_id": "tool_123",
            "timestamp": 1234567890
        }
    
    @patch('time.time')
    def test_add_tool_result_message_with_dict_content(self, mock_time):
        """Test adding a tool result message with dictionary content."""
        mock_time.return_value = 1234567890
        
        manager = MessageManager()
        dict_content = {"results": ["item1", "item2"], "count": 2}
        expected_json = json.dumps(dict_content)
        
        manager.add_tool_result_message(
            tool_name="search",
            content=dict_content,
            tool_call_id="tool_123"
        )
        
        assert len(manager.messages) == 1
        assert manager.messages[0] == {
            "role": "tool_result",
            "content": expected_json,
            "tool_name": "search",
            "tool_call_id": "tool_123",
            "timestamp": 1234567890
        }
    
    @patch('time.time')
    def test_add_tool_result_message_with_serialization_error(self, mock_time):
        """Test adding a tool result message with content that fails to serialize."""
        mock_time.return_value = 1234567890
        
        # Create a class that will cause a serialization error
        class UnserializableObject:
            def __repr__(self):
                return "UnserializableObject()"
        
        with patch('json.dumps', side_effect=TypeError("Object not serializable")):
            manager = MessageManager()
            unserializable_content = UnserializableObject()
            
            manager.add_tool_result_message(
                tool_name="test_tool",
                content=unserializable_content,
                tool_call_id="tool_123"
            )
            
            assert len(manager.messages) == 1
            assert manager.messages[0]["role"] == "tool_result"
            assert manager.messages[0]["content"] == str(unserializable_content)
            assert manager.messages[0]["tool_name"] == "test_tool"
            assert manager.messages[0]["tool_call_id"] == "tool_123"
            assert manager.messages[0]["timestamp"] == 1234567890
    
    def test_get_messages_no_filtering(self):
        """Test getting all messages without filtering."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000},
            {"role": "tool_result", "content": "Tool result", "tool_name": "test_tool", 
             "tool_call_id": "tool_123", "timestamp": 4000}
        ]
        manager.messages = deepcopy(test_messages)
        
        result = manager.get_messages()
        
        # Assert we get a deep copy, not the original messages
        assert result is not manager.messages
        assert result[0] is not manager.messages[0]
        # Assert all messages are returned
        assert len(result) == 4
        assert result == test_messages
    
    def test_get_messages_with_include_roles(self):
        """Test getting messages filtered by include_roles."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000},
            {"role": "tool_result", "content": "Tool result", "tool_name": "test_tool", 
             "tool_call_id": "tool_123", "timestamp": 4000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # Include only 'user' and 'assistant' roles
        result = manager.get_messages(include_roles=["user", "assistant"])
        
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"
    
    def test_get_messages_with_exclude_roles(self):
        """Test getting messages filtered by exclude_roles."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000},
            {"role": "tool_result", "content": "Tool result", "tool_name": "test_tool", 
             "tool_call_id": "tool_123", "timestamp": 4000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # Exclude 'tool_result' and 'system' roles
        result = manager.get_messages(exclude_roles=["tool_result", "system"])
        
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"
    
    def test_get_messages_with_both_include_and_exclude(self):
        """Test getting messages with both include_roles and exclude_roles."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message 1", "timestamp": 1000},
            {"role": "system", "content": "System message 2", "timestamp": 1500},
            {"role": "user", "content": "User message 1", "timestamp": 2000},
            {"role": "user", "content": "User message 2", "timestamp": 2500},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000},
            {"role": "tool_result", "content": "Tool result", "tool_name": "test_tool", 
             "tool_call_id": "tool_123", "timestamp": 4000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # Include 'system' and 'user', but exclude specific system message
        # Include should be applied first, then exclude
        result = manager.get_messages(
            include_roles=["system", "user"],
            exclude_roles=["system"] # This should override include
        )
        
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "user"
    
    def test_get_messages_for_llm_standard_roles(self):
        """Test getting messages formatted for LLM consumption with standard roles."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000}
        ]
        manager.messages = deepcopy(test_messages)
        
        result = manager.get_messages(for_llm=True)
        
        # Standard roles should be preserved but without timestamp
        assert len(result) == 3
        assert result[0] == {"role": "system", "content": "System message"}
        assert result[1] == {"role": "user", "content": "User message"}
        assert result[2] == {"role": "assistant", "content": "Assistant message"}
    
    def test_get_messages_for_llm_with_tool_result(self):
        """Test getting messages formatted for LLM consumption with tool_result role."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "tool_result", "content": "Tool result", "tool_name": "test_tool", 
             "tool_call_id": "tool_123", "timestamp": 3000}
        ]
        manager.messages = deepcopy(test_messages)
        
        result = manager.get_messages(for_llm=True)
        
        # tool_result should be converted to tool with name field
        assert len(result) == 3
        assert result[2] == {
            "role": "tool",
            "content": "Tool result",
            "name": "test_tool",
            "tool_call_id": "tool_123"
        }
    
    def test_get_messages_for_llm_with_filtering(self):
        """Test getting messages formatted for LLM with filtering applied."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000},
            {"role": "tool_result", "content": "Tool result", "tool_name": "test_tool", 
             "tool_call_id": "tool_123", "timestamp": 4000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # Include only 'user' and 'tool_result' roles
        result = manager.get_messages(
            include_roles=["user", "tool_result"],
            for_llm=True
        )
        
        assert len(result) == 2
        assert result[0] == {"role": "user", "content": "User message"}
        assert result[1] == {
            "role": "tool",
            "content": "Tool result",
            "name": "test_tool",
            "tool_call_id": "tool_123"
        }
    
    def test_prune_history_under_limit(self):
        """Test prune_history when message count is under the limit."""
        manager = MessageManager({"max_length": 10})
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000}
        ]
        manager.messages = deepcopy(test_messages)
        
        manager.prune_history()
        
        # No pruning needed, messages should remain unchanged
        assert len(manager.messages) == 2
        assert manager.messages == test_messages
    
    def test_prune_history_remove_oldest_simple(self):
        """Test prune_history with remove_oldest strategy without preserving system messages."""
        manager = MessageManager({"max_length": 2})
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message 1", "timestamp": 2000},
            {"role": "user", "content": "User message 2", "timestamp": 3000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 4000}
        ]
        manager.messages = deepcopy(test_messages)
        
        manager.prune_history(preserve_system=False)
        
        # Should keep only the 2 most recent messages
        assert len(manager.messages) == 2
        assert manager.messages[0]["content"] == "User message 2"
        assert manager.messages[1]["content"] == "Assistant message"
    
    def test_prune_history_remove_oldest_preserve_system(self):
        """Test prune_history with remove_oldest strategy preserving system messages."""
        manager = MessageManager({"max_length": 3})
        test_messages = [
            {"role": "system", "content": "System message 1", "timestamp": 1000},
            {"role": "system", "content": "System message 2", "timestamp": 1500},
            {"role": "user", "content": "User message 1", "timestamp": 2000},
            {"role": "user", "content": "User message 2", "timestamp": 3000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 4000}
        ]
        manager.messages = deepcopy(test_messages)
        
        manager.prune_history(preserve_system=True)
        
        # Should keep all system messages (2) plus the most recent message to reach max_length
        assert len(manager.messages) == 3
        # Check system messages are preserved
        system_messages = [m for m in manager.messages if m["role"] == "system"]
        assert len(system_messages) == 2
        # Check most recent non-system message is preserved
        non_system_messages = [m for m in manager.messages if m["role"] != "system"]
        assert len(non_system_messages) == 1
        assert non_system_messages[0]["content"] == "Assistant message"
    
    def test_prune_history_remove_oldest_prioritize_system_false(self):
        """Test prune_history with remove_oldest when prioritize_system_messages is False."""
        manager = MessageManager({
            "max_length": 2,
            "prioritize_system_messages": False
        })
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # Even with preserve_system=True, it should not prioritize system messages
        # due to the config setting
        manager.prune_history(preserve_system=True)
        
        # Should keep only the 2 most recent messages regardless of role
        assert len(manager.messages) == 2
        assert manager.messages[0]["role"] == "user"
        assert manager.messages[1]["role"] == "assistant"
    
    def test_prune_history_remove_oldest_exact_limit(self):
        """Test prune_history when message count is exactly at the limit."""
        manager = MessageManager({"max_length": 3})
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000}
        ]
        manager.messages = deepcopy(test_messages)
        
        manager.prune_history()
        
        # No pruning needed, messages should remain unchanged
        assert len(manager.messages) == 3
        assert manager.messages == test_messages
    
    def test_prune_history_summarize_fallback(self):
        """Test that prune_history falls back to remove_oldest when strategy is summarize."""
        manager = MessageManager({"max_length": 2, "pruning_strategy": "summarize"})
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # Should log a warning and fall back to remove_oldest
        with patch('logging.Logger.warning') as mock_warning:
            manager.prune_history(preserve_system=True)
            
            # Verify warning was logged
            mock_warning.assert_called_once()
            assert "Summarization not yet implemented" in mock_warning.call_args[0][0]
            
            # Verify fallback to remove_oldest
            assert len(manager.messages) == 2
            assert manager.messages[0]["role"] == "system"
            assert manager.messages[1]["role"] == "assistant"
    
    def test_prune_history_many_system_messages(self):
        """Test prune_history when there are more system messages than max_length."""
        manager = MessageManager({"max_length": 2})
        test_messages = [
            {"role": "system", "content": "System message 1", "timestamp": 1000},
            {"role": "system", "content": "System message 2", "timestamp": 1500},
            {"role": "system", "content": "System message 3", "timestamp": 2000}
        ]
        manager.messages = deepcopy(test_messages)
        
        manager.prune_history(preserve_system=True)
        
        # Should keep all system messages even though it exceeds max_length
        # This is the current behavior of the implementation
        assert len(manager.messages) == 3
        assert all(m["role"] == "system" for m in manager.messages)
    
    def test_clear_history_all_messages(self):
        """Test clearing all message history."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000}
        ]
        manager.messages = deepcopy(test_messages)
        
        manager.clear_history(preserve_system=False)
        
        # All messages should be cleared
        assert len(manager.messages) == 0
    
    def test_clear_history_preserve_system(self):
        """Test clearing history while preserving system messages."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message 1", "timestamp": 1000},
            {"role": "system", "content": "System message 2", "timestamp": 1500},
            {"role": "user", "content": "User message", "timestamp": 2000},
            {"role": "assistant", "content": "Assistant message", "timestamp": 3000}
        ]
        manager.messages = deepcopy(test_messages)
        
        manager.clear_history(preserve_system=True)
        
        # Only system messages should remain
        assert len(manager.messages) == 2
        assert all(m["role"] == "system" for m in manager.messages)
        assert manager.messages[0]["content"] == "System message 1"
        assert manager.messages[1]["content"] == "System message 2"
    
    def test_clear_history_empty(self):
        """Test clearing history when it's already empty."""
        manager = MessageManager()
        
        manager.clear_history()
        
        assert len(manager.messages) == 0
    
    def test_serialize(self):
        """Test serializing the message manager state."""
        config = {
            "max_length": 50,
            "pruning_strategy": "summarize",
            "prioritize_system_messages": False
        }
        manager = MessageManager(config)
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000}
        ]
        manager.messages = deepcopy(test_messages)
        
        serialized = manager.serialize()
        
        # Check that all expected keys are present
        assert "messages" in serialized
        assert "max_history_length" in serialized
        assert "pruning_strategy" in serialized
        assert "prioritize_system_messages" in serialized
        
        # Check that values are correct
        assert serialized["messages"] == test_messages
        assert serialized["max_history_length"] == 50
        assert serialized["pruning_strategy"] == "summarize"
        assert serialized["prioritize_system_messages"] is False
        
        # Check that we got a deep copy, not references
        assert serialized["messages"] is not manager.messages
        assert serialized["messages"][0] is not manager.messages[0]
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid data to restore message manager state."""
        manager = MessageManager()
        
        # Create serialized data
        serialized_data = {
            "messages": [
                {"role": "system", "content": "System message", "timestamp": 1000},
                {"role": "user", "content": "User message", "timestamp": 2000}
            ],
            "max_history_length": 75,
            "pruning_strategy": "remove_oldest",
            "prioritize_system_messages": True
        }
        
        manager.deserialize(serialized_data)
        
        # Check that the state was properly restored
        assert len(manager.messages) == 2
        assert manager.messages[0]["role"] == "system"
        assert manager.messages[1]["role"] == "user"
        assert manager.max_history_length == 75
        assert manager.pruning_strategy == "remove_oldest"
        assert manager.prioritize_system_messages is True
    
    def test_deserialize_incomplete_data(self):
        """Test deserializing incomplete data, should keep defaults for missing fields."""
        manager = MessageManager({
            "max_length": 50,
            "pruning_strategy": "summarize",
            "prioritize_system_messages": False
        })
        
        # Create incomplete serialized data with only messages
        serialized_data = {
            "messages": [
                {"role": "user", "content": "User message", "timestamp": 2000}
            ]
        }
        
        manager.deserialize(serialized_data)
        
        # Check that messages were updated
        assert len(manager.messages) == 1
        assert manager.messages[0]["role"] == "user"
        
        # Check that other fields kept their values
        assert manager.max_history_length == 50
        assert manager.pruning_strategy == "summarize"
        assert manager.prioritize_system_messages is False
    
    def test_deserialize_invalid_data(self):
        """Test deserializing invalid data format, should log error and do nothing."""
        manager = MessageManager()
        original_messages = [
            {"role": "system", "content": "Original system message", "timestamp": 1000}
        ]
        manager.messages = deepcopy(original_messages)
        
        # Try to deserialize non-dict data
        with patch('logging.Logger.error') as mock_error:
            manager.deserialize("not_a_dict")
            
            # Verify error was logged
            mock_error.assert_called_once()
            assert "Invalid deserialization data format" in mock_error.call_args[0][0]
            
            # Verify state was not changed
            assert manager.messages == original_messages
    
    # Edge cases and complex scenarios
    
    def test_get_messages_empty_history(self):
        """Test get_messages with empty history."""
        manager = MessageManager()
        
        result = manager.get_messages()
        
        assert len(result) == 0
        assert result == []
        
        # Even with filtering, should still return empty list
        result_filtered = manager.get_messages(
            include_roles=["user"],
            exclude_roles=["system"],
            for_llm=True
        )
        assert len(result_filtered) == 0
        assert result_filtered == []
    
    def test_prune_history_zero_max_length(self):
        """Test prune_history with zero max_history_length."""
        manager = MessageManager({"max_length": 0})
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # With preserve_system=False, all messages should be removed
        manager.prune_history(preserve_system=False)
        assert len(manager.messages) == 0
        
        # Reset messages
        manager.messages = deepcopy(test_messages)
        
        # With preserve_system=True, system messages are preserved even with max_length=0
        # This is the actual behavior of the current implementation
        manager.prune_history(preserve_system=True)
        assert len(manager.messages) == 2  # All messages are preserved
        assert manager.messages[0]["role"] == "system"
        assert manager.messages[1]["role"] == "user"
    
    def test_get_messages_for_llm_with_invalid_role(self):
        """Test get_messages for LLM with a message that has an unrecognized role."""
        manager = MessageManager()
        test_messages = [
            {"role": "unknown_role", "content": "Message with unknown role", "timestamp": 1000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # Should still format the message, passing through the unrecognized role
        result = manager.get_messages(for_llm=True)
        
        assert len(result) == 1
        assert result[0]["role"] == "unknown_role"
        assert result[0]["content"] == "Message with unknown role"
        assert "timestamp" not in result[0]
    
    def test_add_messages_in_sequence(self):
        """Test adding messages in sequence, verifying correct order and timestamps."""
        with patch('time.time', side_effect=[1000, 2000, 3000, 4000]):
            manager = MessageManager()
            
            manager.add_system_message("System message")
            manager.add_user_message("User message")
            manager.add_assistant_message("Assistant message")
            manager.add_tool_result_message("search", "Tool result", "tool_123")
            
            assert len(manager.messages) == 4
            assert manager.messages[0]["role"] == "system"
            assert manager.messages[0]["timestamp"] == 1000
            assert manager.messages[1]["role"] == "user"
            assert manager.messages[1]["timestamp"] == 2000
            assert manager.messages[2]["role"] == "assistant"
            assert manager.messages[2]["timestamp"] == 3000
            assert manager.messages[3]["role"] == "tool_result"
            assert manager.messages[3]["timestamp"] == 4000
    
    def test_format_for_llm_empty_list(self):
        """Test _format_for_llm with an empty message list."""
        manager = MessageManager()
        
        # Call _format_for_llm directly to test with empty list
        result = manager._format_for_llm([])
        
        assert result == []
    
    def test_get_messages_with_empty_include_roles(self):
        """Test get_messages with empty include_roles list."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message", "timestamp": 1000},
            {"role": "user", "content": "User message", "timestamp": 2000}
        ]
        manager.messages = deepcopy(test_messages)
        
        # According to the implementation, empty include_roles does not filter messages
        # It behaves as if include_roles was not provided
        result = manager.get_messages(include_roles=[])
        
        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"
    
    def test_get_messages_complex_filtering(self):
        """Test get_messages with complex filtering scenario."""
        manager = MessageManager()
        test_messages = [
            {"role": "system", "content": "System message 1", "timestamp": 1000},
            {"role": "system", "content": "System message 2", "timestamp": 1500},
            {"role": "user", "content": "User message 1", "timestamp": 2000},
            {"role": "user", "content": "User message 2", "timestamp": 2500},
            {"role": "assistant", "content": "Assistant message 1", "timestamp": 3000},
            {"role": "assistant", "content": "Assistant message 2", "timestamp": 3500},
            {"role": "tool_result", "content": "Tool result 1", "tool_name": "search", 
             "tool_call_id": "tool_123", "timestamp": 4000},
            {"role": "tool_result", "content": "Tool result 2", "tool_name": "calculator", 
             "tool_call_id": "tool_456", "timestamp": 4500}
        ]
        manager.messages = deepcopy(test_messages)
        
        # Complex filtering scenario: include multiple roles, exclude others, and format for LLM
        result = manager.get_messages(
            include_roles=["user", "assistant", "tool_result"],
            exclude_roles=["assistant"],
            for_llm=True
        )
        
        # Should include user and tool_result messages only
        assert len(result) == 4
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "User message 1"
        assert result[1]["role"] == "user"
        assert result[1]["content"] == "User message 2"
        assert result[2]["role"] == "tool"
        assert result[2]["name"] == "search"
        assert result[3]["role"] == "tool"
        assert result[3]["name"] == "calculator"