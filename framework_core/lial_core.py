from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypedDict, Any, Union

# Message Types
class Message(TypedDict, total=False):
    """
    Represents a chat message in the conversation with an LLM.
    
    Attributes:
        role: The role of the message sender ('system', 'user', 'assistant', or 'tool_result')
        content: The text content of the message
        tool_call_id: Optional ID for a tool call this message is responding to
        tool_name: Optional name of the tool this message is from
    """
    role: str  # 'system', 'user', 'assistant', 'tool_result'
    content: str
    tool_call_id: Optional[str]
    tool_name: Optional[str]

class ToolRequest(TypedDict, total=False):
    """
    Represents a request to execute a tool from the LLM.
    
    Attributes:
        request_id: Unique identifier for this tool request
        tool_name: Name of the tool to execute
        parameters: Parameters for the tool execution
        icerc_full_text: Full ICERC protocol text (Intent, Command, Expected Outcome, Risk Assessment)
    """
    request_id: str
    tool_name: str
    parameters: Dict[str, Any]
    icerc_full_text: str

class LLMResponse(TypedDict):
    """
    Represents a response from the LLM.
    
    Attributes:
        conversation: The conversational text from the LLM
        tool_request: Optional tool request if the LLM wants to execute a tool
    """
    conversation: str
    tool_request: Optional[ToolRequest]

class ToolResult(TypedDict, total=False):
    """
    Represents the result of executing a tool.
    
    Attributes:
        request_id: ID of the original tool request
        tool_name: Name of the tool that was executed
        status: Execution status ('success', 'error', or 'declined_by_user')
        data: The data returned by the tool
    """
    request_id: str
    tool_name: str
    status: str  # 'success', 'error', 'declined_by_user'
    data: Dict[str, Any]

class LLMAdapterInterface(ABC):
    """
    Abstract interface for LLM adapters.
    All specific LLM adapters must implement this interface.
    """
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any], dcm_instance: Any) -> None:
        """
        Initialize the LLM adapter.
        
        Args:
            config: Configuration dictionary with LLM-specific settings
            dcm_instance: Dynamic Context Manager instance for accessing context documents
        """
        pass
    
    @abstractmethod
    def send_message_sequence(
        self, 
        messages: List[Message], 
        active_persona_id: Optional[str] = None
    ) -> LLMResponse:
        """
        Send a sequence of messages to the LLM and get a response.
        
        Args:
            messages: List of Message objects representing the conversation history
            active_persona_id: Optional ID of the active persona to use
        
        Returns:
            LLMResponse containing conversational text and optional tool request
        """
        pass