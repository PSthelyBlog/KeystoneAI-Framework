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