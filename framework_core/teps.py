#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Execution & Permission Service (TEPS)

This module implements the TEPS component of the AI-Assisted Framework V2,
responsible for securely executing tool operations with user permission.

AI-GENERATED: [Forge] - Task:[RFI-TEPS-002]
"""

import os
import subprocess
import shlex
import traceback
from typing import Dict, Any, Optional, List, Union

class TEPSEngine:
    """
    Tool Execution & Permission Service (TEPS) Engine.
    
    This class handles the execution of tool requests from the LLM,
    presenting ICERC information to the user, obtaining user confirmation,
    and executing system operations safely.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, project_root_path: Optional[str] = None):
        """
        Initialize the TEPS Engine.
        
        Args:
            config: Configuration dictionary with optional settings:
                   - allowlist_file: Path to command allowlist file
                   - dry_run_enabled: Whether to enable dry-run option
                   - bash: Bash tool configuration with allowed_commands and blocked_commands
            project_root_path: Root directory path to which file operations will be constrained
        """
        self.config = config or {}
        self.allowlist_enabled = bool(self.config.get("allowlist_file"))
        self.dry_run_enabled = bool(self.config.get("dry_run_enabled", False))
        
        # Load command allowlist/blocklist from configuration
        bash_config = self.config.get("bash", {})
        self.allowed_bash_commands = bash_config.get("allowed_commands", [])
        self.blocked_bash_commands = bash_config.get("blocked_commands", [])
        
        # Configure project root path for file operation security
        if project_root_path and isinstance(project_root_path, str) and project_root_path.strip():
            self.project_root_path = os.path.realpath(os.path.abspath(project_root_path))
            print(f"TEPS: File operations constrained to project root: {self.project_root_path}")
        else:
            self.project_root_path = None
            print("TEPS: Warning - No project root path configured. File path containment checks will be skipped.")
        
        if self.allowlist_enabled:
            self.allowlist = self._load_allowlist(self.config["allowlist_file"])
        else:
            self.allowlist = None
    
    def execute_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool request after displaying ICERC and obtaining user confirmation.
        
        Args:
            tool_request: Dictionary containing the tool request information:
                - request_id: Unique identifier for this request
                - tool_name: Name of the tool to execute
                - parameters: Tool-specific parameters
                - icerc_full_text: Full ICERC protocol text
        
        Returns:
            Dictionary containing the tool execution result:
                - request_id: Same as input request_id
                - tool_name: Same as input tool_name
                - status: "success", "error", or "declined_by_user"
                - data: Tool-specific result data
        """
        # Extract information from the tool request
        request_id = tool_request.get("request_id", "unknown_request")
        tool_name = tool_request.get("tool_name", "unknown_tool")
        parameters = tool_request.get("parameters", {})
        icerc_text = tool_request.get("icerc_full_text", "No ICERC brief provided.")
        
        # For bash commands, validate against allowed/blocked lists before ICERC
        if tool_name == "executeBashCommand":
            command_string = parameters.get("command", "")
            if not command_string:
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {
                        "error_message": "Bash command not specified."
                    }
                }
            
            # Parse command to get the main executable
            try:
                main_command = shlex.split(command_string)[0]
            except Exception as e:
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {
                        "error_message": f"Invalid command format: {str(e)}"
                    }
                }
            
            # Check if command is explicitly blocked
            if self.blocked_bash_commands and main_command in self.blocked_bash_commands:
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {
                        "error_message": f"Command '{main_command}' is explicitly blocked by security policy."
                    }
                }
            
            # Check if command is allowed when allowlist is active
            if self.allowed_bash_commands and main_command not in self.allowed_bash_commands:
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {
                        "error_message": f"Command '{main_command}' is not in the allowed commands list."
                    }
                }
        
        # For file operations, validate path against project root
        elif tool_name in ["readFile", "writeFile"]:
            file_path_param = parameters.get("file_path")
            if not file_path_param:
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {
                        "error_message": "File path not specified."
                    }
                }
            
            # Check if path is within project root
            if not self._is_path_within_project_root(file_path_param):
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {
                        "error_message": f"Access to path '{file_path_param}' is denied. Operation confined to project directory."
                    }
                }
        
        # Display ICERC information to the user
        print("\n=== ICERC PRE-BRIEF ===")
        print(icerc_text)
        print("=======================\n")
        
        # Create a concise action description for the user prompt
        action_description = self._get_action_description(tool_name, parameters)
        
        # Prompt for user confirmation
        user_confirmation = input(f"Proceed with: {action_description}? [Y/N]: ").strip().lower()
        
        # Process user response
        if user_confirmation == 'y':
            # User confirmed, execute the tool
            try:
                # Dispatch to the appropriate handler based on tool name
                if tool_name == "executeBashCommand":
                    result_data = self._handle_bash(parameters)
                elif tool_name == "readFile":
                    result_data = self._handle_readfile(parameters)
                elif tool_name == "writeFile":
                    result_data = self._handle_writefile(parameters)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                # Return success result
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": result_data
                }
            except Exception as e:
                # Return error result with exception details
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {
                        "error_message": str(e),
                        "details": traceback.format_exc()
                    }
                }
        else:
            # User declined, return declined result
            return {
                "request_id": request_id,
                "tool_name": tool_name,
                "status": "declined_by_user",
                "data": {
                    "message": "User declined execution."
                }
            }
    
    def _get_action_description(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Generate a concise description of the action for user confirmation.
        
        Args:
            tool_name: Name of the tool to be executed
            parameters: Parameters for the tool
            
        Returns:
            A human-readable description of the action
        """
        if tool_name == "executeBashCommand":
            return f"BASH: {parameters.get('command', 'Unknown command')}"
        elif tool_name == "readFile":
            return f"READ FILE: {parameters.get('file_path', 'Unknown path')}"
        elif tool_name == "writeFile":
            content_preview = parameters.get('content', '')[:50]
            if len(parameters.get('content', '')) > 50:
                content_preview += "..."
            return f"WRITE FILE: {parameters.get('file_path', 'Unknown path')} ({len(parameters.get('content', ''))} chars)"
        else:
            return f"TOOL: {tool_name} with parameters: {parameters}"
    
    def _handle_bash(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a bash command.
        
        Args:
            parameters: Dictionary containing:
                - command: The bash command to execute
                - working_directory: Optional working directory
        
        Returns:
            Dictionary containing:
                - stdout: Command standard output
                - stderr: Command standard error
                - exit_code: Command exit code
        
        Raises:
            ValueError: If command is not specified or invalid
        """
        # Extract parameters
        command = parameters.get("command")
        cwd = parameters.get("working_directory", os.getcwd())
        
        # Validate command
        if not command:
            raise ValueError("Bash command not specified.")
        
        # Execute command
        process = subprocess.run(
            command, 
            shell=True,  # Required for complex bash commands
            capture_output=True,
            text=True,
            cwd=cwd
        )
        
        # Return result
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "exit_code": process.returncode
        }
    
    def _handle_readfile(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read a file from the filesystem.
        
        Args:
            parameters: Dictionary containing:
                - path: Path to the file to read
                - encoding: Optional file encoding (default: utf-8)
        
        Returns:
            Dictionary containing:
                - file_path: Path to the file that was read
                - content: Content of the file
                
        Raises:
            ValueError: If file path is not specified
            FileNotFoundError: If file doesn't exist
            IOError: If there's an error reading the file
        """
        # Extract parameters
        file_path = parameters.get("file_path")
        encoding = parameters.get("encoding", "utf-8")
        
        # Validate file path
        if not file_path:
            raise ValueError("File path not specified.")
        
        # Read file
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Return result
            return {
                "file_path": file_path,
                "content": content
            }
        except UnicodeDecodeError:
            # If text reading fails, try binary mode and return info
            return {
                "file_path": file_path,
                "content": f"[Binary file, size: {os.path.getsize(file_path)} bytes]",
                "is_binary": True
            }
    
    def _handle_writefile(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            parameters: Dictionary containing:
                - path: Path to the file to write
                - content: Content to write to the file
                - encoding: Optional file encoding (default: utf-8)
                - mode: Optional file mode (default: 'w' for overwrite)
        
        Returns:
            Dictionary containing:
                - file_path: Path to the file that was written
                - status: Status message
                
        Raises:
            ValueError: If file path or content is not specified
            IOError: If there's an error writing to the file
        """
        # Extract parameters
        file_path = parameters.get("file_path")
        content = parameters.get("content", "")
        encoding = parameters.get("encoding", "utf-8")
        mode = parameters.get("mode", "w")  # Default to overwrite
        
        # Validate parameters
        if not file_path:
            raise ValueError("File path not specified.")
        
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Write file
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        # Return result
        return {
            "file_path": file_path,
            "status": "written successfully",
            "bytes_written": len(content.encode(encoding))
        }
    
    def _load_allowlist(self, allowlist_file: str) -> List[str]:
        """
        Load command allowlist from a file.
        
        Args:
            allowlist_file: Path to the allowlist file
            
        Returns:
            List of allowed command patterns
            
        Raises:
            FileNotFoundError: If allowlist file doesn't exist
            IOError: If there's an error reading the allowlist file
        """
        if not os.path.exists(allowlist_file):
            print(f"Warning: Allowlist file {allowlist_file} not found. Allowlist disabled.")
            return []
        
        with open(allowlist_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

    def _is_path_within_project_root(self, target_path_str: str) -> bool:
        """
        Check if the target path is within the configured project root path.
        
        Args:
            target_path_str: The file path to check
            
        Returns:
            Boolean indicating whether the path is within the project root
            Returns True if no project root is configured (validation disabled)
        """
        # If no project root is configured, all paths are allowed
        if self.project_root_path is None:
            print("TEPS: Path validation skipped - no project root configured")
            return True
        
        # Resolve the target path to its absolute, canonical form
        try:
            resolved_target_path = os.path.realpath(os.path.abspath(target_path_str))
            
            # Check if resolved target path is within project root
            # os.path.commonpath returns the longest common subpath of given paths
            # If it equals project_root_path, the target is either the root itself or a subpath
            return os.path.commonpath([self.project_root_path, resolved_target_path]) == self.project_root_path
        
        except (ValueError, TypeError) as e:
            # ValueError can occur if paths are on different drives in Windows
            # TypeError can occur if path is not a string
            print(f"TEPS: Path validation error - {str(e)}")
            return False

if __name__ == "__main__":
    # Simple test if run directly
    print("TEPS Engine - Tool Execution & Permission Service")
    print("This module is not meant to be run directly.")
    print("It should be imported and used by the Framework Core Application.")