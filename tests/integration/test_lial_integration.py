import os
import json
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock

# Import our LIAL components
from framework_core.lial_core import Message, ToolRequest, LLMResponse, ToolResult
from framework_core.adapters.gemini_adapter import GeminiAdapter

# Mock DCM class
class MockDCM:
    def get_document_content(self, doc_id: str) -> Optional[str]:
        if doc_id == "system_instruction":
            return "You are an AI assistant."
        elif doc_id == "persona_catalyst":
            return "You are Catalyst, a strategic AI assistant."
        elif doc_id == "persona_forge":
            return "You are Forge, an implementation AI assistant."
        return None

# Mock TEPS class
class MockTEPS:
    def execute_tool(self, tool_request: ToolRequest) -> ToolResult:
        """Simulate executing a tool based on a tool request."""
        print(f"\nTEPS received tool request: {tool_request['tool_name']}")
        print(f"ICERC text: {tool_request['icerc_full_text']}")
        
        # Simulate user confirmation
        print("TEPS prompting user for confirmation [Y/N]: Y")
        
        # Mock execution results based on tool type
        if tool_request["tool_name"] == "executeBashCommand":
            command = tool_request["parameters"].get("command", "")
            return {
                "request_id": tool_request["request_id"],
                "tool_name": tool_request["tool_name"],
                "status": "success",
                "data": {
                    "stdout": f"Simulated output for: {command}",
                    "stderr": "",
                    "exit_code": 0
                }
            }
        elif tool_request["tool_name"] == "readFile":
            file_path = tool_request["parameters"].get("file_path", "")
            return {
                "request_id": tool_request["request_id"],
                "tool_name": tool_request["tool_name"],
                "status": "success",
                "data": {
                    "content": f"Simulated content of file: {file_path}"
                }
            }
        else:
            return {
                "request_id": tool_request["request_id"],
                "tool_name": tool_request["tool_name"],
                "status": "error",
                "data": {
                    "error": "Unsupported tool"
                }
            }

# Mock Framework Core
class MockFrameworkCore:
    def __init__(self):
        """Initialize the mock framework core with LIAL and TEPS."""
        # Create mock DCM
        self.dcm = MockDCM()
        
        # Create mock TEPS
        self.teps = MockTEPS()
        
        # Configuration for LIAL
        lial_config = {
            "api_key_env_var": "GEMINI_API_KEY",
            "model_name": "gemini-1.5-pro-latest",
            "system_instruction_id": "system_instruction"
        }
        
        # Mock the Gemini API to avoid actual API calls
        self._setup_mock_gemini_api()
        
        # Initialize LIAL with Gemini adapter
        self.lial = GeminiAdapter(config=lial_config, dcm_instance=self.dcm)
    
    def _setup_mock_gemini_api(self):
        """Set up mocks for Gemini API to simulate responses."""
        # This would typically use unittest.mock to patch the Gemini API
        # For this integration test, we'll just replace the send_message_sequence method
        
        # Store the original method
        self._original_send_message = GeminiAdapter.send_message_sequence
        
        # Replace with our mock method
        def mock_send_message(self, messages, active_persona_id=None):
            # Example mock responses based on user input
            user_message = ""
            for msg in messages:
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break
            
            if "list" in user_message.lower() or "ls" in user_message.lower():
                # Simulate a tool request for bash command
                return {
                    "conversation": "I'll list the files for you.",
                    "tool_request": {
                        "request_id": "bash-123",
                        "tool_name": "executeBashCommand",
                        "parameters": {
                            "command": "ls -la",
                            "working_directory": "/home",
                            "icerc_full_text": "Intent: List all files\nCommand: ls -la\nExpected: Directory listing\nRisk: Low"
                        },
                        "icerc_full_text": "Intent: List all files\nCommand: ls -la\nExpected: Directory listing\nRisk: Low"
                    }
                }
            elif "read" in user_message.lower() or "open" in user_message.lower():
                # Simulate a tool request for reading a file
                return {
                    "conversation": "I'll read that file for you.",
                    "tool_request": {
                        "request_id": "read-456",
                        "tool_name": "readFile",
                        "parameters": {
                            "file_path": "/example/file.txt",
                            "icerc_full_text": "Intent: Read file\nCommand: Read /example/file.txt\nExpected: File contents\nRisk: Low"
                        },
                        "icerc_full_text": "Intent: Read file\nCommand: Read /example/file.txt\nExpected: File contents\nRisk: Low"
                    }
                }
            elif any(msg.get("role") == "tool_result" for msg in messages):
                # This is a response after a tool execution
                tool_message = next((msg for msg in messages if msg.get("role") == "tool_result"), None)
                if tool_message:
                    tool_name = tool_message.get("tool_name", "unknown")
                    if tool_name == "executeBashCommand":
                        return {
                            "conversation": "I've executed the command. Here are the results from the directory listing.",
                            "tool_request": None
                        }
                    elif tool_name == "readFile":
                        return {
                            "conversation": "I've read the file. Here is the content.",
                            "tool_request": None
                        }
            
            # Default response for unrecognized inputs
            return {
                "conversation": f"I'm sorry, I don't understand how to '{user_message}'.",
                "tool_request": None
            }
        
        # Apply the mock
        GeminiAdapter.send_message_sequence = mock_send_message
    
    def cleanup(self):
        """Restore original methods after testing."""
        # Restore the original method
        GeminiAdapter.send_message_sequence = self._original_send_message
    
    def process_user_input(self, user_input: str, active_persona: Optional[str] = "forge"):
        """Process user input through the LIAL-TEPS flow."""
        print(f"\n--- Processing User Input: '{user_input}' ---")
        
        # Step 1: Send user input to LIAL
        print("\nStep 1: Sending user message to LIAL")
        messages = [{"role": "user", "content": user_input}]
        llm_response = self.lial.send_message_sequence(messages, active_persona_id=active_persona)
        
        # Step 2: Display the conversational response
        print(f"\nStep 2: Received LLM conversation response:")
        print(f"'{llm_response['conversation']}'")
        
        # Step 3: Check for tool requests
        tool_request = llm_response.get("tool_request")
        if tool_request:
            print("\nStep 3: LLM requested a tool execution")
            
            # Step 4: Send the tool request to TEPS
            print("\nStep 4: Sending tool request to TEPS")
            tool_result = self.teps.execute_tool(tool_request)
            
            # Step 5: Send the tool result back to LIAL
            print(f"\nStep 5: Sending tool result back to LIAL:")
            print(f"Status: {tool_result['status']}")
            print(f"Data: {json.dumps(tool_result['data'], indent=2)}")
            
            # Create a tool result message
            tool_message = {
                "role": "tool_result",
                "content": json.dumps(tool_result["data"]),
                "tool_name": tool_result["tool_name"],
                "tool_call_id": tool_result["request_id"]
            }
            
            # Add the message to the conversation
            messages.append({"role": "assistant", "content": llm_response["conversation"]})
            messages.append(tool_message)
            
            # Get the next response from LIAL
            print("\nStep 6: Getting next response from LIAL")
            next_response = self.lial.send_message_sequence(messages, active_persona_id=active_persona)
            
            # Display the next conversational response
            print(f"\nStep 7: Final LLM response:")
            print(f"'{next_response['conversation']}'")
        else:
            print("\nNo tool execution requested")

# Main integration test function
def run_integration_test():
    print("=== LIAL Integration Test ===")
    
    # Check if the API key is set (for demonstration only)
    if "GEMINI_API_KEY" not in os.environ:
        # Set a dummy API key for testing
        os.environ["GEMINI_API_KEY"] = "dummy_api_key_for_testing"
        print("Set dummy API key for testing")
    
    # Create the mock framework core
    core = MockFrameworkCore()
    
    try:
        # Test case 1: Simple conversation (no tool requests)
        core.process_user_input("What is the weather like today?")
        
        # Test case 2: Command execution
        core.process_user_input("List the files in the current directory")
        
        # Test case 3: File reading
        core.process_user_input("Read the file at /example/file.txt")
    finally:
        # Clean up
        core.cleanup()
    
    print("\n=== Integration Test Complete ===")

if __name__ == "__main__":
    run_integration_test()