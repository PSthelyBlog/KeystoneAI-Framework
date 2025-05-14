# TEPS: Tool Execution & Permission Service

**Version:** 1.0.0  
**Author:** `Forge` (as part of RFI-TEPS-002)  
**Date:** 2025-05-13  

## 1. Overview

The Tool Execution & Permission Service (TEPS) is a core component of the AI-Assisted Framework V2 that handles the secure execution of system operations requested by LLMs. TEPS implements the ICERC protocol (Intent, Command, Expected Outcome, Risk Assessment, Confirmation Request), displaying relevant information to the user and requiring explicit confirmation before performing any system-altering operation.

## 2. Key Features

- Processing tool requests from the Framework Core Application
- Displaying ICERC information to users
- Obtaining explicit user confirmation for operations
- Executing system operations (bash commands, file I/O)
- Error handling and reporting
- Optional command allowlist functionality

## 3. Component Architecture

TEPS is implemented as a Python class `TEPSEngine` within the `framework_core/teps.py` module. It is designed to be instantiated by the Framework Core Application and interact with the LIAL and DCM components as part of the overall system.

![TEPS Architecture](../migration_planning_v2/M_Migration_Architecture_v2.md#L15-L36)

## 4. Implementation Details

### 4.1. Data Flow

The typical data flow for a tool execution is as follows:

1. The Framework Core Application receives a `ToolRequest` from LIAL.
2. The Core App calls `teps.execute_tool(tool_request)`.
3. TEPS displays the ICERC pre-brief text to the user and prompts for confirmation.
4. If the user confirms, TEPS executes the operation and captures results.
5. TEPS returns a standardized `ToolResult` to the Core App.
6. The Core App formats this result for LIAL to send back to the LLM.

### 4.2. Class Interface

```python
class TEPSEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Initialize with optional configuration
        
    def execute_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        # Main method to execute a tool request
        # Returns a tool result dictionary
```

### 4.3. Tool Request Format

Tool requests are dictionaries with the following structure:

```python
{
    "request_id": "unique_request_id",
    "tool_name": "executeBashCommand" | "readFile" | "writeFile",
    "parameters": {
        # Tool-specific parameters
        # For executeBashCommand:
        "command": "ls -la",
        "working_directory": "/optional/path"
        
        # For readFile:
        "path": "/path/to/file.txt",
        "encoding": "utf-8"  # optional
        
        # For writeFile:
        "path": "/path/to/file.txt",
        "content": "Content to write",
        "encoding": "utf-8",  # optional
        "mode": "w"  # optional, 'w' for overwrite, 'a' for append
    },
    "icerc_full_text": "Full text of ICERC protocol (Intent, Command, Expected, Risk)"
}
```

### 4.4. Tool Result Format

Tool results are dictionaries with the following structure:

```python
{
    "request_id": "same_as_input_request_id",
    "tool_name": "same_as_input_tool_name",
    "status": "success" | "error" | "declined_by_user",
    "data": {
        # Tool-specific result data
        # For executeBashCommand:
        "stdout": "Command output",
        "stderr": "Error output if any",
        "exit_code": 0  # or other exit code
        
        # For readFile:
        "file_path": "/path/to/file.txt",
        "content": "File content"
        
        # For writeFile:
        "file_path": "/path/to/file.txt",
        "status": "written successfully",
        "bytes_written": 123
        
        # For errors:
        "error_message": "Error description",
        "details": "Stack trace or other details"
        
        # For declined operations:
        "message": "User declined execution."
    }
}
```

## 5. Supported Tools

TEPS currently supports the following tools:

### 5.1. `executeBashCommand`

Executes a bash shell command.

**Parameters:**
- `command` (required): The bash command to execute
- `working_directory` (optional): Working directory for command execution

**Returns:**
- `stdout`: Standard output from the command
- `stderr`: Standard error from the command
- `exit_code`: Command exit code

### 5.2. `readFile`

Reads content from a file.

**Parameters:**
- `path` (required): Path to the file to read
- `encoding` (optional): File encoding (default: utf-8)

**Returns:**
- `file_path`: Path to the file that was read
- `content`: Content of the file

### 5.3. `writeFile`

Writes content to a file.

**Parameters:**
- `path` (required): Path to the file to write
- `content` (required): Content to write to the file
- `encoding` (optional): File encoding (default: utf-8)
- `mode` (optional): File mode (default: 'w' for overwrite)

**Returns:**
- `file_path`: Path to the file that was written
- `status`: Status message
- `bytes_written`: Number of bytes written

## 6. Security Considerations

The TEPS component implements several security measures:

1. **ICERC Protocol**: Displays Intent, Command, Expected Outcome, and Risk Assessment to the user.
2. **Explicit User Confirmation**: Requires Y/N confirmation before any operation.
3. **Error Containment**: Catches and properly handles errors to prevent system crashes.
4. **Optional Command Allowlist**: Can be configured to only allow certain commands.

## 7. Configuration Options

TEPS accepts an optional configuration dictionary with the following options:

```python
config = {
    "allowlist_file": "/path/to/allowlist.txt",  # Path to command allowlist file
    "dry_run_enabled": True  # Enable dry-run functionality
}
```

## 8. Integration with Framework Core

To integrate TEPS into the Framework Core Application:

```python
from framework_core.teps import TEPSEngine

# Initialize TEPS
teps = TEPSEngine(config)

# When an LLM generates a tool request:
tool_request = {...}  # Received from LIAL
tool_result = teps.execute_tool(tool_request)
# Send tool_result back to LIAL
```

## 9. Testing

TEPS includes comprehensive unit and integration tests:

- **Unit Tests**: `/tests/unit/framework_core/test_teps.py`
- **Integration Tests**: `/tests/integration/test_teps_integration.py`

Run tests using pytest:

```bash
pytest tests/unit/framework_core/test_teps.py -v
pytest tests/integration/test_teps_integration.py -v
```

## 10. Future Enhancements

Potential future enhancements for TEPS include:

1. Enhanced allowlist functionality with pattern matching
2. Support for additional tool types
3. Configurable permission levels
4. Detailed logging and auditing
5. Implement "Dry Run" option for bash commands

## 11. Conclusion

The TEPS component provides a secure and flexible mechanism for executing system operations in the AI-Assisted Framework. By implementing the ICERC protocol and requiring explicit user confirmation, it ensures that LLMs cannot perform potentially harmful operations without user approval.