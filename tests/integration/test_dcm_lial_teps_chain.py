#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for the DCM-LIAL-TEPS component chain.

These tests verify that the Dynamic Context Manager (DCM), 
LLM Interaction Abstraction Layer (LIAL), and
Tool Execution & Permission Service (TEPS) components work together correctly.

AI-GENERATED: [Forge] - Task:[RFI-COREAPP-INT-TEST-001]
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock the google.generativeai module before importing GeminiAdapter
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

from framework_core.dcm import DynamicContextManager
from framework_core.lial_core import LLMAdapterInterface, Message, LLMResponse, ToolRequest
from framework_core.teps import ToolExecutionService
from framework_core.component_managers.dcm_manager import DCMManager
from framework_core.component_managers.lial_manager import LIALManager
from framework_core.component_managers.teps_manager import TEPSManager


class MockLLMAdapter(LLMAdapterInterface):
    """Mock LLM Adapter for testing the integration chain."""
    
    def __init__(self, config: dict, dcm_instance=None) -> None:
        """Initialize the mock adapter with configuration and DCM."""
        self.config = config
        self.dcm = dcm_instance
        self.messages_sent = []
        self.persona_used = None
        self.response_to_return = None
    
    def send_message_sequence(self, messages: list, active_persona_id: str = None) -> dict:
        """Mock sending a message sequence to the LLM."""
        self.messages_sent.append(messages)
        self.persona_used = active_persona_id
        
        # Get persona content if available
        persona_info = ""
        if active_persona_id and self.dcm:
            persona_content = self.dcm.get_document_content(active_persona_id)
            if persona_content:
                persona_info = f" with persona content: {len(persona_content)} chars"
        
        # Return predetermined response if set, otherwise generate a default
        if self.response_to_return:
            return self.response_to_return
        
        # Look for tool request keywords in the last user message
        last_user_message = next((m["content"] for m in reversed(messages) 
                                 if m["role"] == "user"), "")
        
        if "file" in last_user_message.lower():
            return {
                "conversation": f"I'll read that file for you{persona_info}.",
                "tool_request": {
                    "request_id": "req123",
                    "tool_name": "read_file",
                    "parameters": {
                        "file_path": "/test/file.txt"
                    }
                }
            }
        elif "command" in last_user_message.lower():
            return {
                "conversation": f"I'll execute that command{persona_info}.",
                "tool_request": {
                    "request_id": "req456",
                    "tool_name": "bash",
                    "parameters": {
                        "command": "echo 'Hello World'"
                    }
                }
            }
        else:
            return {
                "conversation": f"This is a default response{persona_info}.",
                "tool_request": None
            }
    
    def set_response(self, response: dict) -> None:
        """Set a predetermined response for the next call."""
        self.response_to_return = response


class TestDCMLIALTEPSChain(unittest.TestCase):
    """Test cases for the DCM-LIAL-TEPS component chain integration."""
    
    def setUp(self):
        """Set up test environment with temporary directory and test files."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test structure and files
        os.makedirs(os.path.join(self.temp_dir, "personas"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "standards"), exist_ok=True)
        
        # Create persona file
        with open(os.path.join(self.temp_dir, "personas", "test_persona.md"), 'w', encoding='utf-8') as f:
            f.write("# Test Persona\n\nThis is a test persona for integration testing.")
        
        # Create standard file
        with open(os.path.join(self.temp_dir, "standards", "test_standard.md"), 'w', encoding='utf-8') as f:
            f.write("# Test Standard\n\nThis is a test standard.")
        
        # Create test file that will be accessed via read_file tool
        with open(os.path.join(self.temp_dir, "test_file.txt"), 'w', encoding='utf-8') as f:
            f.write("This is a test file content.")
        
        # Create context definition file
        self.context_file_path = os.path.join(self.temp_dir, "FRAMEWORK_CONTEXT.md")
        with open(self.context_file_path, 'w', encoding='utf-8') as f:
            f.write("""# Framework Context Definition

# initial_prompt_template: "You are an AI assistant using test_persona."

## Personas
persona_test: @./personas/test_persona.md

## Standards
standard_test: @./standards/test_standard.md
""")
        
        # Initialize real DCM with test files
        self.dcm = DynamicContextManager(self.context_file_path)
        
        # Create DCM Manager
        self.dcm_manager = DCMManager({"definition_path": self.context_file_path})
        
        # Initialize mock LLM adapter with DCM
        self.mock_llm_adapter = MockLLMAdapter({
            "api_key": "test_key",
            "model": "test-model"
        }, self.dcm)
        
        # Create LIAL Manager with mock adapter
        self.lial_manager = LIALManager({
            "provider": "test",
            "settings": {
                "api_key": "test_key",
                "model": "test-model"
            }
        }, self.dcm_manager)
        
        # Replace the adapter factory in LIAL manager
        self.lial_manager._create_llm_adapter = MagicMock(return_value=self.mock_llm_adapter)
        self.lial_manager._adapter = self.mock_llm_adapter
        
        # Initialize mock TEPS
        self.mock_teps = MagicMock(spec=ToolExecutionService)
        self.mock_teps.execute_tool.return_value = {
            "request_id": "test123",
            "tool_name": "test_tool",
            "status": "success",
            "data": {
                "result": "Tool execution successful"
            }
        }
        
        # Create TEPS Manager with mock TEPS
        self.teps_manager = TEPSManager({
            "allowed_tools": ["read_file", "write_file", "bash"],
            "confirmation_required": True
        })
        self.teps_manager._teps = self.mock_teps
    
    def tearDown(self):
        """Clean up temporary files and directories."""
        shutil.rmtree(self.temp_dir)
    
    def test_context_loading_to_lial(self):
        """Test that DCM correctly loads context and provides it to LIAL."""
        # Verify DCM loaded the context correctly
        self.assertIsNotNone(self.dcm.get_document_content("persona_test"))
        
        # Create message and send through LIAL
        messages = [{"role": "user", "content": "Hello"}]
        response = self.lial_manager.send_messages(messages, "persona_test")
        
        # Verify that persona was passed to the LLM adapter
        self.assertEqual(self.mock_llm_adapter.persona_used, "persona_test")
    
    def test_lial_tool_request_to_teps(self):
        """Test that LIAL can generate tool requests that are executed by TEPS."""
        # Configure LLM to generate a tool request
        self.mock_llm_adapter.set_response({
            "conversation": "I'll execute that command.",
            "tool_request": {
                "request_id": "cmd123",
                "tool_name": "bash",
                "parameters": {
                    "command": "echo 'test'"
                }
            }
        })
        
        # Configure TEPS with expected response
        self.mock_teps.execute_tool.return_value = {
            "request_id": "cmd123",
            "tool_name": "bash",
            "status": "success",
            "data": {
                "output": "test",
                "exit_code": 0
            }
        }
        
        # Send message through LIAL
        messages = [{"role": "user", "content": "Run a test command"}]
        response = self.lial_manager.send_messages(messages)
        
        # Extract the tool request from the response
        tool_request = response["tool_request"]
        self.assertIsNotNone(tool_request)
        
        # Execute the tool request through TEPS
        tool_result = self.teps_manager.execute_tool(tool_request)
        
        # Verify TEPS was called with the correct request
        self.mock_teps.execute_tool.assert_called_once()
        self.assertEqual(self.mock_teps.execute_tool.call_args[0][0]["tool_name"], "bash")
        self.assertEqual(self.mock_teps.execute_tool.call_args[0][0]["parameters"]["command"], "echo 'test'")
        
        # Verify the result is correct
        self.assertEqual(tool_result["status"], "success")
        self.assertEqual(tool_result["data"]["output"], "test")
    
    def test_full_chain_file_reading_flow(self):
        """Test the complete flow from DCM to LIAL to TEPS for reading a file."""
        # Configure TEPS file read response
        self.mock_teps.execute_tool.side_effect = lambda req: {
            "request_id": req["request_id"],
            "tool_name": req["tool_name"],
            "status": "success",
            "data": {
                "content": "This is a test file content.",
                "file_path": req["parameters"]["file_path"]
            }
        } if req["tool_name"] == "read_file" else {
            "request_id": req["request_id"],
            "tool_name": req["tool_name"],
            "status": "success",
            "data": {
                "result": "Generic tool execution successful"
            }
        }
        
        # First message gets a tool request
        messages = [
            {"role": "system", "content": self.dcm.get_initial_prompt_template()},
            {"role": "user", "content": "Please read a file for me"}
        ]
        
        # Get response from LIAL (should contain tool request)
        response1 = self.lial_manager.send_messages(messages, "persona_test")
        
        # Verify persona was used
        self.assertEqual(self.mock_llm_adapter.persona_used, "persona_test")
        
        # Extract tool request
        tool_request = response1["tool_request"]
        self.assertIsNotNone(tool_request)
        self.assertEqual(tool_request["tool_name"], "read_file")
        
        # Execute tool via TEPS
        tool_result = self.teps_manager.execute_tool(tool_request)
        
        # Verify TEPS was called with correct request
        self.assertEqual(tool_result["tool_name"], "read_file")
        self.assertEqual(tool_result["status"], "success")
        self.assertEqual(tool_result["data"]["content"], "This is a test file content.")
        
        # Add result to messages
        messages.append({"role": "assistant", "content": response1["conversation"]})
        messages.append({
            "role": "tool_result",
            "tool_name": "read_file",
            "content": tool_result["data"]["content"],
            "status": "success"
        })
        
        # Configure LIAL for follow-up response
        self.mock_llm_adapter.set_response({
            "conversation": "I've read the file and it contains: This is a test file content.",
            "tool_request": None
        })
        
        # Send follow-up messages with tool result
        response2 = self.lial_manager.send_messages(messages, "persona_test")
        
        # Verify response integrates the tool result
        self.assertIn("I've read the file", response2["conversation"])
        self.assertIn("test file content", response2["conversation"])
        self.assertIsNone(response2["tool_request"])
    
    def test_full_chain_command_execution_flow(self):
        """Test the complete flow from DCM to LIAL to TEPS for executing a command."""
        # Configure TEPS command execution response
        self.mock_teps.execute_tool.side_effect = lambda req: {
            "request_id": req["request_id"],
            "tool_name": req["tool_name"],
            "status": "success",
            "data": {
                "output": "Command executed successfully",
                "exit_code": 0,
                "command": req["parameters"]["command"]
            }
        } if req["tool_name"] == "bash" else {
            "request_id": req["request_id"],
            "tool_name": req["tool_name"],
            "status": "success",
            "data": {
                "result": "Generic tool execution successful"
            }
        }
        
        # First message gets a tool request
        messages = [
            {"role": "system", "content": self.dcm.get_initial_prompt_template()},
            {"role": "user", "content": "Run a command for me"}
        ]
        
        # Get response from LIAL (should contain tool request)
        response1 = self.lial_manager.send_messages(messages, "persona_test")
        
        # Extract tool request
        tool_request = response1["tool_request"]
        self.assertIsNotNone(tool_request)
        self.assertEqual(tool_request["tool_name"], "bash")
        
        # Execute tool via TEPS
        tool_result = self.teps_manager.execute_tool(tool_request)
        
        # Verify TEPS was called with correct request
        self.assertEqual(tool_result["tool_name"], "bash")
        self.assertEqual(tool_result["status"], "success")
        self.assertEqual(tool_result["data"]["output"], "Command executed successfully")
        
        # Add result to messages
        messages.append({"role": "assistant", "content": response1["conversation"]})
        messages.append({
            "role": "tool_result",
            "tool_name": "bash",
            "content": tool_result["data"]["output"],
            "status": "success"
        })
        
        # Configure LIAL for follow-up response
        self.mock_llm_adapter.set_response({
            "conversation": "The command execution was successful with output: Command executed successfully",
            "tool_request": None
        })
        
        # Send follow-up messages with tool result
        response2 = self.lial_manager.send_messages(messages, "persona_test")
        
        # Verify response integrates the tool result
        self.assertIn("command execution was successful", response2["conversation"])
        self.assertIsNone(response2["tool_request"])
    
    def test_error_handling_in_chain(self):
        """Test error handling and propagation through the component chain."""
        # Configure TEPS to return an error
        self.mock_teps.execute_tool.return_value = {
            "request_id": "error123",
            "tool_name": "read_file",
            "status": "error",
            "error": {
                "message": "File not found",
                "code": "FILE_NOT_FOUND"
            }
        }
        
        # Configure LIAL to generate a tool request
        self.mock_llm_adapter.set_response({
            "conversation": "I'll read that file for you.",
            "tool_request": {
                "request_id": "error123",
                "tool_name": "read_file",
                "parameters": {
                    "file_path": "/non/existent/file.txt"
                }
            }
        })
        
        # Send message through LIAL
        messages = [{"role": "user", "content": "Read a non-existent file"}]
        response1 = self.lial_manager.send_messages(messages)
        
        # Extract the tool request
        tool_request = response1["tool_request"]
        self.assertIsNotNone(tool_request)
        
        # Execute the tool request (should result in error)
        tool_result = self.teps_manager.execute_tool(tool_request)
        
        # Verify result is an error
        self.assertEqual(tool_result["status"], "error")
        self.assertEqual(tool_result["error"]["code"], "FILE_NOT_FOUND")
        
        # Add result to messages
        messages.append({"role": "assistant", "content": response1["conversation"]})
        messages.append({
            "role": "tool_result",
            "tool_name": "read_file",
            "content": "Error: File not found",
            "status": "error",
            "error": tool_result["error"]
        })
        
        # Configure LIAL for follow-up response
        self.mock_llm_adapter.set_response({
            "conversation": "I'm sorry, I couldn't read the file because it was not found.",
            "tool_request": None
        })
        
        # Send follow-up messages with tool error
        response2 = self.lial_manager.send_messages(messages)
        
        # Verify response acknowledges the error
        self.assertIn("couldn't read the file", response2["conversation"])
        self.assertIn("not found", response2["conversation"])
    
    def test_multiple_personas_across_sessions(self):
        """Test the chain works correctly with different personas in different sessions."""
        # Create an additional persona
        with open(os.path.join(self.temp_dir, "personas", "another_persona.md"), 'w', encoding='utf-8') as f:
            f.write("# Another Persona\n\nThis is another test persona.")
        
        # Update context file with the new persona
        with open(self.context_file_path, 'w', encoding='utf-8') as f:
            f.write("""# Framework Context Definition

# initial_prompt_template: "You are an AI assistant using the selected persona."

## Personas
persona_test: @./personas/test_persona.md
persona_another: @./personas/another_persona.md

## Standards
standard_test: @./standards/test_standard.md
""")
        
        # Reinitialize DCM to load the updated context
        self.dcm = DynamicContextManager(self.context_file_path)
        self.dcm_manager = DCMManager({"definition_path": self.context_file_path})
        
        # Reset the mock adapter's DCM
        self.mock_llm_adapter.dcm = self.dcm
        
        # Session 1: Use persona_test
        messages1 = [{"role": "user", "content": "Hello from session 1"}]
        response1 = self.lial_manager.send_messages(messages1, "persona_test")
        
        # Verify persona_test was used
        self.assertEqual(self.mock_llm_adapter.persona_used, "persona_test")
        
        # Session 2: Use persona_another
        messages2 = [{"role": "user", "content": "Hello from session 2"}]
        response2 = self.lial_manager.send_messages(messages2, "persona_another")
        
        # Verify persona_another was used
        self.assertEqual(self.mock_llm_adapter.persona_used, "persona_another")
        
        # Verify both personas were correctly loaded by DCM
        self.assertIsNotNone(self.dcm.get_document_content("persona_test"))
        self.assertIsNotNone(self.dcm.get_document_content("persona_another"))
        
        # Session 3: No persona (should not use any persona)
        messages3 = [{"role": "user", "content": "Hello from session 3"}]
        response3 = self.lial_manager.send_messages(messages3)
        
        # Verify no persona was used
        self.assertIsNone(self.mock_llm_adapter.persona_used)


if __name__ == "__main__":
    unittest.main()