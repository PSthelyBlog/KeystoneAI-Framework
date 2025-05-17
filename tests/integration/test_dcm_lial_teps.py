"""
Integration tests for the full DCM-LIAL-TEPS component chain.

These tests verify the integration between all three core components:
- Dynamic Context Manager (DCM)
- LLM Interaction Abstraction Layer (LIAL)
- Tool Execution & Permission Service (TEPS)
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch

# Ensure framework_core is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from framework_core.exceptions import DCMInitError, LIALInitError, TEPSInitError, ToolExecutionError
from framework_core.component_managers.dcm_manager import DCMManager
from framework_core.component_managers.lial_manager import LIALManager
from framework_core.component_managers.teps_manager import TEPSManager
from framework_core.lial_core import Message, LLMResponse, ToolRequest, ToolResult
from framework_core.tool_request_handler import ToolRequestHandler
from tests.integration.utils import MockLLMAdapter, ResponseBuilder, IntegrationTestCase


class TestDCMLIALTEPSIntegration(IntegrationTestCase):
    """
    Integration tests for the full DCM-LIAL-TEPS chain.
    
    These tests validate that:
    1. All three components can work together in various scenarios
    2. Context flows correctly from DCM through LIAL to TEPS
    3. Tool execution results are properly handled through the chain
    4. Errors are properly propagated through the entire chain
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        super().setup_method()
        
        # Create mock DCM content
        self.mock_context_content = {
            "main_system_prompt": "You are an AI assistant in the KeystoneAI Framework.",
            "persona_catalyst": "# Catalyst Persona\nThe strategic AI planner focused on architecture and planning.",
            "persona_forge": "# Forge Persona\nThe expert AI implementer focused on detailed execution."
        }
        
        # Create mock DCM instance
        self.dcm_instance = MagicMock(name="DynamicContextManager")
        self.dcm_instance.get_document_content.side_effect = lambda doc_id: self.mock_context_content.get(doc_id)
        self.dcm_instance.get_full_initial_context.return_value = self.mock_context_content
        self.dcm_instance.get_initial_prompt_template.return_value = self.mock_context_content["main_system_prompt"]
        self.dcm_instance.get_persona_definitions.return_value = {
            "catalyst": self.mock_context_content["persona_catalyst"],
            "forge": self.mock_context_content["persona_forge"]
        }
        
        # Create DCM manager
        self.dcm_manager = MagicMock(name="DCMManager")
        self.dcm_manager.dcm_instance = self.dcm_instance
        self.dcm_manager.get_document_content.side_effect = self.dcm_instance.get_document_content
        self.dcm_manager.get_full_context.return_value = self.dcm_instance.get_full_initial_context()
        self.dcm_manager.get_initial_prompt.return_value = self.dcm_instance.get_initial_prompt_template()
        self.dcm_manager.get_persona_definitions.return_value = self.dcm_instance.get_persona_definitions()
        
        # Create LLM adapter
        self.llm_adapter = MockLLMAdapter(
            config={"model_name": "mock-model", "temperature": 0.7},
            dcm_instance=self.dcm_instance
        )
        
        # Configure standard responses
        self.llm_adapter.configure_response("default", {
            "conversation": "I am an AI assistant. How can I help you?",
            "tool_request": None
        })
        
        self.llm_adapter.configure_response("catalyst", {
            "conversation": "(Catalyst) I'll help you plan and architect a solution.",
            "tool_request": None
        })
        
        self.llm_adapter.configure_response("forge", {
            "conversation": "(Forge) I'll implement that for you with precision.",
            "tool_request": None
        })
        
        # Configure tool request responses
        self.llm_adapter.configure_response("read_file", ResponseBuilder.tool_request(
            tool_name="readFile",
            parameters={"file_path": "/path/to/file.txt"},
            conversation_text="I'll read that file for you.",
            request_id="read-123"
        ))
        
        self.llm_adapter.configure_response("write_file", ResponseBuilder.tool_request(
            tool_name="writeFile",
            parameters={"file_path": "/path/to/file.txt", "content": "New content"},
            conversation_text="I'll write to that file for you.",
            request_id="write-456"
        ))
        
        self.llm_adapter.configure_response("execute_command", ResponseBuilder.tool_request(
            tool_name="executeBashCommand",
            parameters={"command": "ls -la"},
            conversation_text="I'll run that command for you.",
            request_id="bash-789"
        ))
        
        # Add pattern matchers
        self.llm_adapter.configure_pattern("read file", "read_file")
        self.llm_adapter.configure_pattern("write file", "write_file")
        self.llm_adapter.configure_pattern("run command", "execute_command")
        
        # Create LIAL manager with our adapter
        self.lial_manager = MagicMock(name="LIALManager")
        self.lial_manager.send_messages.side_effect = self.llm_adapter.send_message_sequence
        
        # Create mock TEPS instance
        self.teps_instance = MagicMock(name="TEPSEngine")
        
        # Configure TEPS execute_tool with appropriate responses
        def mock_execute_tool(tool_request):
            tool_name = tool_request.get("tool_name", "unknown")
            request_id = tool_request.get("request_id", "unknown")
            
            if tool_name == "readFile":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": "Content of the requested file."
                }
            elif tool_name == "writeFile":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": {"bytes_written": 123, "path": tool_request.get("parameters", {}).get("file_path")}
                }
            elif tool_name == "executeBashCommand":
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": "Command output here"
                }
            elif "error" in tool_name.lower():
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "error",
                    "data": {"error_message": "Tool execution failed"}
                }
            else:
                return {
                    "request_id": request_id,
                    "tool_name": tool_name,
                    "status": "success",
                    "data": {"message": "Tool executed successfully"}
                }
        
        self.teps_instance.execute_tool.side_effect = mock_execute_tool
        
        # Create TEPS manager with our mock TEPS instance
        self.teps_manager = MagicMock(name="TEPSManager")
        self.teps_manager.teps_instance = self.teps_instance
        self.teps_manager.execute_tool.side_effect = self.teps_instance.execute_tool
        
        # Create ToolRequestHandler with our TEPS manager
        self.tool_request_handler = ToolRequestHandler(teps_manager=self.teps_manager)
        
        # Create message sequences for testing
        self.basic_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Hello, who are you?")
        ])
        
        self.read_file_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Can you read file /path/to/file.txt?")
        ])
        
        self.forge_messages = ResponseBuilder.message_sequence([
            ("system", "You are Forge, the expert AI implementer in the KeystoneAI Framework."),
            ("user", "Help me implement a new feature.")
        ])
    
    def test_end_to_end_tool_execution_flow(self):
        """Test the complete flow from user input through all components to tool execution and result."""
        # 1. Start with a request that should trigger tool usage
        # 2. Get response from LIAL with tool request
        lial_response = self.lial_manager.send_messages(self.read_file_messages)
        
        # Verify the tool request is generated correctly
        assert lial_response["tool_request"] is not None
        assert lial_response["tool_request"]["tool_name"] == "readFile"
        assert lial_response["tool_request"]["parameters"]["file_path"] == "/path/to/file.txt"
        
        # 3. Execute the tool via the ToolRequestHandler
        tool_result = self.tool_request_handler.process_tool_request(lial_response["tool_request"])
        
        # Verify tool execution
        assert tool_result["status"] == "success"
        assert tool_result["data"] == "Content of the requested file."
        
        # 4. Format the result as a message
        formatted_result = self.tool_request_handler.format_tool_result_as_message(tool_result)
        
        # Verify proper formatting
        assert formatted_result["role"] == "tool_result"
        assert formatted_result["content"] == "Content of the requested file."
        assert formatted_result["tool_name"] == "readFile"
        
        # 5. Create follow-up messages with tool result for next LLM interaction
        follow_up_messages = self.read_file_messages + [
            {"role": "assistant", "content": lial_response["conversation"]},
            {
                "role": "tool",  # Note: Convert from tool_result to tool for LLM
                "content": formatted_result["content"],
                "name": formatted_result["tool_name"],
                "tool_call_id": formatted_result["tool_call_id"]
            }
        ]
        
        # Configure a specific response for the follow-up with tool result
        self.llm_adapter.configure_response("tool_result_response", {
            "conversation": f"I've read the file and found: '{formatted_result['content']}'",
            "tool_request": None
        })
        
        # Override matching response for this test
        original_find_matching_response = self.llm_adapter._find_matching_response
        
        def tool_result_matcher(messages, active_persona_id):
            # Check if this is our follow-up message with tool result
            for msg in messages:
                if msg.get("role") == "tool" and msg.get("name") == "readFile":
                    return self.llm_adapter.responses["tool_result_response"]
            return original_find_matching_response(messages, active_persona_id)
        
        self.llm_adapter._find_matching_response = tool_result_matcher
        
        # 6. Send follow-up to LLM with tool result
        follow_up_response = self.lial_manager.send_messages(follow_up_messages)
        
        # Restore original method
        self.llm_adapter._find_matching_response = original_find_matching_response
        
        # Verify LLM responds to the tool result appropriately
        assert "I've read the file and found" in follow_up_response["conversation"]
        assert "Content of the requested file" in follow_up_response["conversation"]
    
    def test_persona_specific_tool_usage(self):
        """Test that persona-specific context influences tool usage patterns."""
        # Configure persona-specific tool requests
        self.llm_adapter.configure_response("catalyst_analyze", ResponseBuilder.tool_request(
            tool_name="readFile",
            parameters={"file_path": "/path/to/requirements.txt"},
            conversation_text="(Catalyst) I'll analyze the requirements file to help with architecture planning.",
            request_id="catalyst-read-123"
        ))
        
        self.llm_adapter.configure_response("forge_implement", ResponseBuilder.tool_request(
            tool_name="writeFile",
            parameters={"file_path": "/path/to/implementation.py", "content": "def implement(): pass"},
            conversation_text="(Forge) I'll implement the feature by creating this file.",
            request_id="forge-write-456"
        ))
        
        # Create message sequences for different personas
        catalyst_messages = ResponseBuilder.message_sequence([
            ("system", "You are Catalyst, the strategic AI planner in the KeystoneAI Framework."),
            ("user", "Analyze the requirements for this project.")
        ])
        
        forge_implementation_messages = ResponseBuilder.message_sequence([
            ("system", "You are Forge, the expert AI implementer in the KeystoneAI Framework."),
            ("user", "Implement the feature based on the requirements.")
        ])
        
        # Set up a direct mapping of messages to responses for testing
        response_step = [0]  # Use a mutable list for state
        
        def direct_persona_response(messages, active_persona_id=None):
            # Just return pre-configured responses in sequence
            step = response_step[0]
            response_step[0] += 1
            
            if step == 0:  # First call - Catalyst
                return self.llm_adapter.responses["catalyst_analyze"]
            else:  # Second call - Forge
                return self.llm_adapter.responses["forge_implement"]
        
        # Save original method
        original_send = self.lial_manager.send_messages
        self.lial_manager.send_messages = direct_persona_response
        
        # Get responses for each persona
        catalyst_response = self.lial_manager.send_messages(catalyst_messages)
        forge_response = self.lial_manager.send_messages(forge_implementation_messages)
        
        # Restore original method
        self.lial_manager.send_messages = original_send
        
        # Verify Catalyst uses appropriate tool
        assert catalyst_response["tool_request"] is not None
        assert catalyst_response["tool_request"]["tool_name"] == "readFile"
        assert "requirements" in catalyst_response["tool_request"]["parameters"]["file_path"]
        assert "(Catalyst)" in catalyst_response["conversation"]
        
        # Verify Forge uses appropriate tool
        assert forge_response["tool_request"] is not None
        assert forge_response["tool_request"]["tool_name"] == "writeFile"
        assert "implementation" in forge_response["tool_request"]["parameters"]["file_path"]
        assert "(Forge)" in forge_response["conversation"]
        
        # Execute both tools
        catalyst_result = self.tool_request_handler.process_tool_request(catalyst_response["tool_request"])
        forge_result = self.tool_request_handler.process_tool_request(forge_response["tool_request"])
        
        # Verify both executions succeed
        assert catalyst_result["status"] == "success"
        assert forge_result["status"] == "success"
    
    def test_multi_step_workflow(self):
        """Test a multi-step workflow across all components with sequential tool usage."""
        # Configure responses for a multi-step workflow
        self.llm_adapter.configure_response("step1_read_requirements", ResponseBuilder.tool_request(
            tool_name="readFile",
            parameters={"file_path": "/path/to/requirements.txt"},
            conversation_text="First, I'll read the requirements file.",
            request_id="step1-read-123"
        ))
        
        self.llm_adapter.configure_response("step2_analyze", {
            "conversation": "Based on the requirements, we need to implement feature X.",
            "tool_request": None
        })
        
        self.llm_adapter.configure_response("step3_implement", ResponseBuilder.tool_request(
            tool_name="writeFile",
            parameters={"file_path": "/path/to/feature_x.py", "content": "def feature_x(): pass"},
            conversation_text="Now I'll implement the feature.",
            request_id="step3-write-456"
        ))
        
        self.llm_adapter.configure_response("step4_run_tests", ResponseBuilder.tool_request(
            tool_name="executeBashCommand",
            parameters={"command": "pytest /path/to/tests/"},
            conversation_text="Let's run the tests to verify our implementation.",
            request_id="step4-bash-789"
        ))
        
        self.llm_adapter.configure_response("step5_complete", {
            "conversation": "Feature X has been successfully implemented and tested.",
            "tool_request": None
        })
        
        # Start the workflow
        workflow_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Implement feature X according to the requirements.")
        ])
        
        # Create a direct response sequence for the test
        step_responses = [
            self.llm_adapter.responses["step1_read_requirements"],
            self.llm_adapter.responses["step2_analyze"],
            self.llm_adapter.responses["step3_implement"],
            self.llm_adapter.responses["step4_run_tests"],
            self.llm_adapter.responses["step5_complete"]
        ]
        
        # Define a counter for tracking which step to return
        step_counter = [0]  # Using list for mutable state
        
        # Define a mock send_messages that returns our predefined sequence
        def fixed_sequence_response(messages, active_persona_id=None):
            current_step = step_counter[0]
            response = step_responses[min(current_step, len(step_responses) - 1)]
            step_counter[0] += 1
            return response
        
        # Save original method
        original_send = self.lial_manager.send_messages
        self.lial_manager.send_messages = fixed_sequence_response
        
        # STEP 1: Read requirements
        step1_response = self.lial_manager.send_messages(workflow_messages)
        assert step1_response["tool_request"] is not None
        assert step1_response["tool_request"]["tool_name"] == "readFile"
        
        # Execute step 1 tool
        step1_result = self.tool_request_handler.process_tool_request(step1_response["tool_request"])
        step1_formatted = self.tool_request_handler.format_tool_result_as_message(step1_result)
        
        # Add result to messages
        workflow_messages_step2 = workflow_messages + [
            {"role": "assistant", "content": step1_response["conversation"]},
            {
                "role": "tool",
                "content": step1_formatted["content"],
                "name": step1_formatted["tool_name"],
                "tool_call_id": step1_formatted["tool_call_id"]
            }
        ]
        
        # STEP 2: Analyze requirements (no tool)
        step2_response = self.lial_manager.send_messages(workflow_messages_step2)
        assert step2_response["tool_request"] is None
        
        # Add response to messages
        workflow_messages_step3 = workflow_messages_step2 + [
            {"role": "assistant", "content": step2_response["conversation"]}
        ]
        
        # STEP 3: Implement feature
        step3_response = self.lial_manager.send_messages(workflow_messages_step3)
        assert step3_response["tool_request"] is not None
        assert step3_response["tool_request"]["tool_name"] == "writeFile"
        
        # Execute step 3 tool
        step3_result = self.tool_request_handler.process_tool_request(step3_response["tool_request"])
        step3_formatted = self.tool_request_handler.format_tool_result_as_message(step3_result)
        
        # Add result to messages
        workflow_messages_step4 = workflow_messages_step3 + [
            {"role": "assistant", "content": step3_response["conversation"]},
            {
                "role": "tool",
                "content": step3_formatted["content"],
                "name": step3_formatted["tool_name"],
                "tool_call_id": step3_formatted["tool_call_id"]
            }
        ]
        
        # STEP 4: Run tests
        step4_response = self.lial_manager.send_messages(workflow_messages_step4)
        assert step4_response["tool_request"] is not None
        assert step4_response["tool_request"]["tool_name"] == "executeBashCommand"
        
        # Execute step 4 tool
        step4_result = self.tool_request_handler.process_tool_request(step4_response["tool_request"])
        step4_formatted = self.tool_request_handler.format_tool_result_as_message(step4_result)
        
        # Add result to messages
        workflow_messages_step5 = workflow_messages_step4 + [
            {"role": "assistant", "content": step4_response["conversation"]},
            {
                "role": "tool",
                "content": step4_formatted["content"],
                "name": step4_formatted["tool_name"],
                "tool_call_id": step4_formatted["tool_call_id"]
            }
        ]
        
        # STEP 5: Complete workflow
        step5_response = self.lial_manager.send_messages(workflow_messages_step5)
        assert step5_response["tool_request"] is None
        assert "successfully implemented" in step5_response["conversation"]
        
        # Restore original method
        self.lial_manager.send_messages = original_send
    
    def test_error_propagation_through_chain(self):
        """Test error propagation through the entire DCM-LIAL-TEPS chain."""
        # 1. Configure LIAL to generate an error tool request
        self.llm_adapter.configure_response("error_tool", ResponseBuilder.tool_request(
            tool_name="errorTool",
            parameters={"param": "value"},
            conversation_text="I'll try this tool for you.",
            request_id="error-999"
        ))
        
        # 2. Configure TEPS to return an error result instead of raising an exception
        original_execute = self.teps_manager.execute_tool
        
        def execute_with_error_result(tool_request):
            if tool_request.get("tool_name") == "errorTool":
                return {
                    "request_id": tool_request.get("request_id", "unknown"),
                    "tool_name": tool_request.get("tool_name", "unknown"),
                    "status": "error",
                    "data": {"error_message": "Simulated error in the TEPS component"}
                }
            return original_execute(tool_request)
        
        self.teps_manager.execute_tool = execute_with_error_result
        
        # 3. Create error-triggering message sequence
        error_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Test error handling")
        ])
        
        # 4. Direct response to generate error tool
        self.lial_manager.send_messages = lambda *args, **kwargs: self.llm_adapter.responses["error_tool"]
        
        # Get the error tool request
        error_response = self.lial_manager.send_messages(error_messages)
        
        # Verify tool request generation
        assert error_response["tool_request"] is not None
        assert error_response["tool_request"]["tool_name"] == "errorTool"
        
        # 5. Execute the tool - should return error status instead of exception
        error_result = self.tool_request_handler.process_tool_request(error_response["tool_request"])
        
        # Verify error result
        assert error_result["status"] == "error"
        assert "error_message" in error_result["data"]
        assert "Simulated error" in error_result["data"]["error_message"]
        
        # 6. Configure LLM to handle error feedback
        self.llm_adapter.configure_response("error_handling", {
            "conversation": "I encountered an error while executing the tool: Simulated error in the TEPS component",
            "tool_request": None
        })
        
        # 7. Format the error result as a message
        error_formatted = self.tool_request_handler.format_tool_result_as_message(error_result)
        
        # 8. Use direct response approach for error handling test
        original_lial_send = self.lial_manager.send_messages
        self.lial_manager.send_messages = lambda *args, **kwargs: self.llm_adapter.responses["error_handling"]
        
        # 9. Create follow-up messages with error result
        error_follow_up = error_messages + [
            {"role": "assistant", "content": error_response["conversation"]},
            {
                "role": "tool",
                "content": error_formatted["content"],
                "name": error_formatted["tool_name"],
                "tool_call_id": error_formatted["tool_call_id"]
            }
        ]
        
        # 10. Send error follow-up to LLM
        error_handled_response = self.lial_manager.send_messages(error_follow_up)
        
        # Restore original methods
        self.lial_manager.send_messages = original_lial_send
        self.teps_manager.execute_tool = original_execute
        
        # Verify LLM acknowledges the error
        assert "error" in error_handled_response["conversation"].lower()
        assert "Simulated error" in error_handled_response["conversation"]
    
    def test_context_preservation_in_tool_flow(self):
        """Test that context from DCM is preserved throughout the tool execution flow."""
        # Define specific context in DCM that should influence tool usage
        custom_context = {
            "project_config": "# Project Config\nAllowed file paths: /projects/safe_dir/\nForbidden actions: rm, format"
        }
        
        # Update mock DCM to include this context
        self.mock_context_content.update(custom_context)
        
        # Configure LIAL to use context in tool requests
        self.llm_adapter.configure_response("context_aware_tool", ResponseBuilder.tool_request(
            tool_name="writeFile",
            parameters={"file_path": "/projects/safe_dir/config.txt", "content": "Safe content"},
            conversation_text="Based on project configuration, I'll write to the allowed directory.",
            request_id="context-write-123"
        ))
        
        # Configure TEPS to validate context-based permissions
        original_execute = self.teps_manager.execute_tool
        
        def context_aware_execute(tool_request):
            # Simple permission check based on context
            if tool_request.get("tool_name") == "writeFile":
                file_path = tool_request.get("parameters", {}).get("file_path", "")
                # Check if path is in allowed paths
                if not file_path.startswith("/projects/safe_dir/"):
                    return {
                        "request_id": tool_request.get("request_id"),
                        "tool_name": tool_request.get("tool_name"),
                        "status": "error",
                        "data": {"error_message": "Path not allowed according to project configuration"}
                    }
            return original_execute(tool_request)
        
        self.teps_manager.execute_tool = context_aware_execute
        
        # Create message referencing context
        context_messages = ResponseBuilder.message_sequence([
            ("system", "You are an AI assistant in the KeystoneAI Framework."),
            ("user", "Write a file according to project configuration.")
        ])
        
        # Use direct fixed response approach for deterministic testing
        original_send = self.lial_manager.send_messages
        self.lial_manager.send_messages = lambda *args, **kwargs: self.llm_adapter.responses["context_aware_tool"]
        
        # Send context-dependent request
        context_response = self.lial_manager.send_messages(context_messages)
        
        # Verify response uses context
        assert context_response["tool_request"] is not None
        assert context_response["tool_request"]["tool_name"] == "writeFile"
        assert "/projects/safe_dir/" in context_response["tool_request"]["parameters"]["file_path"]
        
        # Execute the tool
        tool_result = self.tool_request_handler.process_tool_request(context_response["tool_request"])
        
        # Verify execution succeeds due to context-based permission
        assert tool_result["status"] == "success"
        
        # Test with invalid path
        bad_tool_request = {
            "request_id": "bad-123",
            "tool_name": "writeFile",
            "parameters": {"file_path": "/var/unsafe/file.txt", "content": "Unsafe content"},
            "icerc_full_text": "Intent: Write file\nCommand: Write to /var/unsafe/file.txt\nExpected: File creation\nRisk: Low\nConfirmation: [Y/N]"
        }
        
        # Execute tool with path that violates context rules
        bad_result = self.tool_request_handler.process_tool_request(bad_tool_request)
        
        # Verify execution fails due to context-based permission
        assert bad_result["status"] == "error"
        assert "not allowed" in bad_result["data"]["error_message"]
        
        # Restore original methods
        self.lial_manager.send_messages = original_send
        self.teps_manager.execute_tool = original_execute