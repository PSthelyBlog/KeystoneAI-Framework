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