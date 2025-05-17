# Framework Core Application - Integration Test Plan

**Version:** 1.0  
**Date:** 2025-05-17  
**Author:** Forge  
**Related RFI:** RFI-TEST-INTEGRATION-PLAN-001  

## 1. Introduction & Objectives

### 1.1. Purpose of Integration Testing

The KeystoneAI-Framework represents a complex multi-component system built on the LLM Agnostic Core Architecture (LACA). This architecture enables human-AI-AI collaboration through well-defined components that must work together seamlessly:

- The **Dynamic Context Manager (DCM)** loads and provides contextual information
- The **LLM Interaction Abstraction Layer (LIAL)** handles communication with AI models
- The **Tool Execution & Permission Service (TEPS)** manages system operations
- The **Framework Controller** orchestrates the entire system
- Supporting components including **MessageManager**, **UIManager**, and **ToolRequestHandler**

While unit tests verify individual component behavior, integration testing is essential to validate that these components interact correctly as a unified system. This document outlines a comprehensive plan for integration testing the KeystoneAI-Framework, focusing on component interactions, data flow, and end-to-end scenarios.

### 1.2. Key Objectives

The primary objectives of this integration testing effort are to:

1. **Verify Component Interaction Integrity**: Ensure all LACA components collaborate correctly according to the defined interfaces.

2. **Validate Data Flow**: Confirm that data structures (Messages, ToolRequests, ToolResults, LLMResponses) flow correctly between components, maintaining integrity throughout the processing chain.

3. **Test Error Propagation**: Verify that errors originating in one component are properly handled, logged, and communicated to dependent components and ultimately to the user.

4. **Exercise Critical User Scenarios**: Test the most important end-to-end usage patterns with mocked external dependencies (LLM APIs, file system, terminal I/O).

5. **Ensure Initialization Integrity**: Validate that the system initializes correctly with various configuration options and properly loads all required components.

6. **Confirm Graceful Error Handling**: Test the system's ability to maintain stability and provide meaningful feedback when errors occur at component boundaries.

7. **Assess Persona Switching**: Verify the correct handling of persona switching between Catalyst and Forge roles during system operation.

## 2. Integration Test Scope

The scope of integration testing encompasses:

1. **Component Interface Compatibility**: Verifying that component interfaces correctly interact with one another.
2. **Data Flow**: Ensuring that data flows correctly between components.
3. **Error Handling**: Testing error propagation and recovery across component boundaries.
4. **End-to-End Workflows**: Testing complete workflow scenarios from user input to final output.
5. **Resource Management**: Ensuring resources are properly managed across component interactions.

## 3. Integration Test Strategy & Approach

### 3.1. Testing Philosophy

The integration testing strategy for the KeystoneAI-Framework follows these core principles:

1. **Component-Chain Focus**: Tests should verify entire component interaction chains rather than just interface boundaries.
2. **Scenario-Based Testing**: Prioritize real-world scenarios that exercise multiple components in concert.
3. **Mocked External Interfaces**: All external systems (LLM APIs, file system, terminal I/O) should be consistently mocked.
4. **Resilience Testing**: Explicitly verify system behavior under error conditions at each component boundary.
5. **Persona-Aware Testing**: Test different behaviors when interacting with the Catalyst vs. Forge personas.

### 3.2. Integration Testing Levels

The integration testing effort is organized into three primary levels, with each level focusing on specific aspects of component interaction:

#### 3.2.1. Component-to-Component Integration

Tests focused on verifying direct interfaces between two adjacent components:

* **Test Scope**: Interface contracts, data transformations, error propagation
* **Isolation**: All other components are mocked
* **Coverage Focus**: Interface method signatures, parameter validation, return types

#### 3.2.2. Component Chain Integration

Tests that verify multi-component workflows through partial system integrations:

* **Test Scope**: End-to-end data flow across 3+ components
* **Isolation**: Only external interfaces (LLM API, file system) are mocked
* **Coverage Focus**: Data transformation chains, sequential processing flows

#### 3.2.3. Full-System Integration

Tests that verify the entire system works together with mocked external dependencies:

* **Test Scope**: Complete user interactions, full initialization sequences
* **Isolation**: Only LLM API, file system, and terminal I/O are mocked
* **Coverage Focus**: End-to-end workflows, system-level error handling

### 3.3. Testing Approach & Methodology

#### 3.3.1. Test Environment Setup

The integration testing environment consists of:

* **Testing Framework**: `pytest` with plugin support for mocking and coverage measurement
* **Mocking Libraries**: 
  * `unittest.mock` for Python object mocking
  * `pyfakefs` for file system virtualization
  * Custom mock adapters for LLM APIs
* **Project Location**: Tests will be organized in the `/tests/integration/` directory, with subdirectories for different test categories
* **Common Fixtures**: 
  * Shared configuration fixtures
  * Mock response fixtures
  * Common test data

#### 3.3.2. Implementation Approach

The development of integration tests will follow this structured approach:

1. **Bottom-Up Implementation**:
   * Start with component-to-component integration tests
   * Progress to component chain integration tests
   * Finally, implement full-system integration tests

2. **Fixture-Based Test Design**:
   * Create comprehensive fixtures for mock responses and test data
   * Use pytest fixture composition for test setup
   * Organize fixtures in shared modules for reuse

3. **Contextual Mocking**:
   * Use context managers for mocking in specific test scopes
   * Create specialized mock factories for different test scenarios
   * Implement verification helpers to confirm mock interactions

4. **Hybrid Black-Box/White-Box Testing**:
   * Primarily black-box testing through component interfaces
   * Limited white-box testing for verifying internal state when necessary
   * Internal state verification only when essential for test validation

#### 3.3.3. Test Coverage Goals

The integration test suite aims to achieve:

* **Interaction Coverage**: 100% coverage of all defined component interfaces
* **Workflow Coverage**: 100% coverage of user-facing workflows
* **Error Path Coverage**: 85%+ coverage of error paths and recovery scenarios
* **Code Coverage**: >80% line coverage for the framework code through integration tests

#### 3.3.4. Test Categorization

Integration tests will be organized into the following categories:

1. **Core Component Chain Tests**:
   * DCM → LIAL chain tests
   * LIAL → TEPS chain tests
   * Full DCM → LIAL → TEPS chain tests
   * MessageManager integration tests
   * ToolRequestHandler integration tests

2. **Controller-Focused Tests**:
   * Initialization and workflow coordination
   * Command processing and routing
   * Error handling and recovery

3. **End-to-End User Flow Tests**:
   * Conversation-only scenarios
   * Tool execution scenarios
   * Special command processing
   * Error handling and user feedback

4. **Configuration and Initialization Tests**:
   * Various configuration scenarios
   * Component initialization sequences
   * Configuration validation

#### 3.3.5. Testing Tools and Utilities

Custom testing utilities will be developed to support integration testing:

1. **MockLLMAdapter**: A configurable adapter implementing the `LLMAdapterInterface` that returns predetermined responses
2. **ResponseBuilder**: Utilities to construct valid response structures for different test scenarios
3. **IntegrationTestCase**: Base class with common setup and assertion methods for integration tests
4. **MockInput/OutputCapture**: Utilities for terminal I/O mocking and verification

## 4. Test Data and Mocking Strategy

### 4.1. Mocking Strategy

#### 4.1.1. LLM Adapter Mocking

The LIAL component's LLM adapters (e.g., GeminiAdapter) will be mocked to allow controlled testing without actual API calls:

1. **Mock LLM Response Generation**:
   - Create a `MockLLMAdapter` class that implements `LLMAdapterInterface`
   - Configure the mock adapter to return predefined responses based on input patterns
   - Support both conversation-only responses and tool request responses

2. **Persona-Aware Responses**:
   - Mock different responses based on the active persona (Catalyst or Forge)
   - Include logic to handle persona switching requests appropriately

3. **Error Simulation**:
   - Add functionality to simulate various error conditions (API errors, timeouts, malformed responses)
   - Create response templates that include intentional format errors for testing error handling

Example mock implementation approach:
```python
class MockLLMAdapter(LLMAdapterInterface):
    def __init__(self, config: Dict, dcm_instance):
        self.responses = {
            "default": {"conversation": "Default response", "tool_request": None},
            "weather_query": {"conversation": "Let me check the weather", 
                             "tool_request": {"tool_name": "weather", 
                                             "parameters": {"location": "New York"}}},
            "file_read": {"conversation": "I'll check that file for you", 
                         "tool_request": {"tool_name": "readFile", 
                                         "parameters": {"file_path": "/path/to/file"}}}
        }
        self.error_responses = {
            "api_error": Exception("API Error"),
            "timeout": TimeoutError("Request timed out"),
            "malformed": {"invalid": "format"}
        }
        
    def send_message_sequence(self, messages: List[Message], 
                             active_persona_id: Optional[str]) -> LLMResponse:
        # Pattern matching logic to determine appropriate response
        # based on message content and active persona
```

#### 4.1.2. File System & TEPS Mocking

For TEPS integration testing, mock the actual system operations:

1. **Mock File System**:
   - Use `pyfakefs` or similar libraries to create a virtual file system
   - Pre-populate with test files needed for test scenarios
   - Capture file operations for verification

2. **Mock Bash Command Execution**:
   - Create a controlled environment for bash command execution
   - Pre-define outputs for specific commands
   - Verify command parameters and flags

3. **ICERC Pre-brief Handling**:
   - Mock the user confirmation process for ICERC prompts
   - Configure different confirmation responses (Y/N/Dry-Run) for different test scenarios

#### 4.1.3. UI Manager Mocking

Mock terminal I/O for automated testing:

1. **Input Mocking**:
   - Create predefined input sequences including special commands
   - Simulate user interrupts (Ctrl+C) and empty inputs
   - Support multiline input simulation

2. **Output Verification**:
   - Capture all output text for verification
   - Verify formatting of different message types (system, user, assistant, error)
   - Test display handling for various terminal widths

#### 4.1.4. DCM Mocking

For tests that don't focus on DCM functionality:

1. **Mock Document Loading**:
   - Pre-define content for foundational documents
   - Avoid actual file system dependencies

### 4.2. Test Data Requirements

#### 4.2.1. Sample Message Sequences

Create comprehensive test fixtures for message sequences:

1. **Basic Conversation**:
   ```python
   basic_conversation = [
       {"role": "system", "content": "You are an AI assistant."},
       {"role": "user", "content": "Hello, how are you?"},
       {"role": "assistant", "content": "I'm doing well! How can I help you today?"}
   ]
   ```

2. **Tool Request Flow**:
   ```python
   tool_request_flow = [
       {"role": "system", "content": "You are Forge, the implementer."},
       {"role": "user", "content": "Read the file at /path/to/file.txt"},
       {"role": "assistant", "content": "I'll read that file for you."},
       # Tool request would be generated here by the LLM
       {"role": "tool_result", "content": "File contents here", 
        "tool_name": "readFile", "tool_call_id": "12345"}
   ]
   ```

3. **Error Handling Flow**:
   ```python
   error_flow = [
       {"role": "system", "content": "You are Catalyst, the strategist."},
       {"role": "user", "content": "Execute this invalid command"},
       {"role": "assistant", "content": "I'll try to execute that."},
       {"role": "tool_result", "content": "Error: Command not found", 
        "tool_name": "executeCommand", "tool_call_id": "67890"}
   ]
   ```

#### 4.2.2. Tool Request Templates

Define standardized tool request templates for each supported tool:

1. **File Operations**:
   ```python
   read_file_request = {
       "request_id": "read-123",
       "tool_name": "readFile",
       "parameters": {"file_path": "/path/to/file.txt"},
       "icerc_full_text": "Intent: Read file contents\nCommand: Read file at /path/to/file.txt\nExpected: File contents will be displayed\nRisk: Low, read-only operation\nConfirmation: Please confirm [Y/N]"
   }
   
   write_file_request = {
       "request_id": "write-456",
       "tool_name": "writeFile",
       "parameters": {"file_path": "/path/to/file.txt", "content": "New content"},
       "icerc_full_text": "Intent: Create/update file\nCommand: Write to /path/to/file.txt\nExpected: File will be created/updated\nRisk: Medium, existing file will be overwritten\nConfirmation: Please confirm [Y/N]"
   }
   ```

2. **Bash Commands**:
   ```python
   bash_command_request = {
       "request_id": "bash-789",
       "tool_name": "executeBashCommand",
       "parameters": {"command": "ls -la"},
       "icerc_full_text": "Intent: List directory contents\nCommand: ls -la\nExpected: Directory listing\nRisk: Low, read-only operation\nConfirmation: Please confirm [Y/N]"
   }
   ```

#### 4.2.3. Configuration Test Cases

Create multiple configuration scenarios to test initialization:

1. **Minimal Valid Configuration**:
   ```yaml
   llm_provider: "mock"
   context_definition_file: "/path/to/FRAMEWORK_CONTEXT.md"
   ```

2. **Complete Configuration**:
   ```yaml
   llm_provider: "mock"
   context_definition_file: "/path/to/FRAMEWORK_CONTEXT.md"
   llm_settings:
     mock:
       temperature: 0.7
       max_tokens: 1000
   teps_settings:
     bash:
       allowed_commands: ["ls", "echo", "cat"]
     dry_run_enabled: true
   ui_settings:
     prompt_prefix: "> "
   message_history_settings:
     max_messages: 100
   ```

3. **Invalid Configuration Cases**:
   - Missing required fields
   - Invalid field values
   - Unsupported provider
   - Non-existent file paths

#### 4.2.4. Mock LLM Response Templates

Create a library of mock LLM responses for different scenarios:

1. **Persona-Specific Responses**:
   ```python
   catalyst_response = {
       "conversation": "(Catalyst) Based on our strategic analysis, I recommend the following approach...",
       "tool_request": None
   }
   
   forge_response = {
       "conversation": "(Forge) I'll implement that feature by creating the following files...",
       "tool_request": {"tool_name": "writeFile", "parameters": {...}}
   }
   ```

2. **Tool Request Responses**:
   ```python
   file_read_response = {
       "conversation": "Let me read that file for you.",
       "tool_request": {
           "request_id": "tool-123",
           "tool_name": "readFile",
           "parameters": {"file_path": "/path/to/file.txt"},
           "icerc_full_text": "Intent: Read file for analysis\nCommand: Read /path/to/file.txt\nExpected: File contents will be shown\nRisk: Low, read-only operation\nConfirmation: Please confirm [Y/N]"
       }
   }
   ```

3. **Error and Edge Cases**:
   - Malformed responses
   - Missing fields
   - Unexpected content types

## 5. Key Integration Scenarios

This section outlines the critical integration scenarios that the test suite will cover. These scenarios exercise multiple components working together and focus on key user workflows and system behaviors.

### 5.1. Core Component Chain Scenarios

These scenarios test the essential component chains at the heart of the LACA model.

#### 5.1.1. Framework Initialization and Initial Prompt

**Scenario Description:**  
Test the complete initialization flow of the framework from configuration loading to initial system prompt generation.

**Components Involved:**  
`ConfigurationManager` → `FrameworkController` → `DCMManager` → `LIALManager` → `TEPSManager` → `MessageManager` → `UIManager`

**Test Flow:**
1. Mock configuration loading for all components
2. Verify proper initialization sequence and dependency handling
3. Confirm DCM correctly loads the context and provides the initial prompt
4. Verify the initial prompt is correctly added to MessageManager
5. Validate UIManager displays the welcome message
6. Assert all components are fully initialized and in the expected state

**Expected Outcomes:**
- All components initialize successfully and in the correct order
- Initial prompt is correctly loaded from DCM and added to message history
- UIManager displays the expected welcome message
- FrameworkController enters the running state

**Error Paths to Test:**
- Missing or invalid configuration file
- Non-existent context definition file
- Initialization failure of each component

#### 5.1.2. User Input to LLM Text Response

**Scenario Description:**  
Test the complete flow from user input to LLM processing to text response display.

**Components Involved:**  
`UIManager` → `FrameworkController` → `MessageManager` → `LIALManager` (mocked) → `MessageManager` → `UIManager`

**Test Flow:**
1. Initialize all required components
2. Configure MockLLMAdapter to return a simple text-only response
3. Submit user input through UIManager
4. Trace flow through FrameworkController to MessageManager
5. Verify message history is updated with user message
6. Confirm LIALManager receives the correct message sequence
7. Validate FrameworkController correctly processes LLM response
8. Check MessageManager properly stores assistant response
9. Assert UIManager displays the assistant response correctly

**Expected Outcomes:**
- User input is correctly captured and stored in message history
- LIALManager receives properly formatted message sequence
- Assistant response is correctly processed and displayed
- Message history is properly updated with both user and assistant messages

**Error Paths to Test:**
- Invalid or empty user input
- LLM connection failure
- Malformed LLM response

#### 5.1.3. Full Tool Call Cycle

**Scenario Description:**  
Test the complete cycle from user input through tool request generation, execution, and result processing.

**Components Involved:**  
`UIManager` → `FrameworkController` → `MessageManager` → `LIALManager` (mocked) → `ToolRequestHandler` → `TEPSManager` → `MessageManager` → `LIALManager` → `UIManager`

**Test Flow:**
1. Initialize all required components
2. Configure MockLLMAdapter to return a tool request (e.g., reading a file)
3. Submit user input that would trigger tool use
4. Trace flow through the Framework to MessageManager
5. Configure TEPS to return a successful tool result
6. Verify message history updates with tool result
7. Configure MockLLMAdapter for a follow-up response processing the tool result
8. Assert UIManager displays the final response

**Expected Outcomes:**
- Tool request is correctly generated and routed to TEPS
- ICERC brief is properly formatted and would be displayed to user
- Tool result is executed and result captured
- Tool result is properly added to message history
- Follow-up LLM response correctly integrates tool result
- Final response is displayed to user

**Error Paths to Test:**
- Tool execution failure
- User rejection of tool execution
- Invalid tool parameters
- Malformed tool request from LLM

#### 5.1.4. DCM-LIAL Context Integration

**Scenario Description:**  
Test that the Dynamic Context Manager correctly provides persona context to LIAL.

**Components Involved:**  
`DCMManager` → `LIALManager` (mocked) → `FrameworkController`

**Test Flow:**
1. Configure DCM with test context files for both Catalyst and Forge personas
2. Initialize LIAL with the DCM instance
3. Send messages through LIAL with each persona ID
4. Verify LIAL correctly utilizes the appropriate persona context

**Expected Outcomes:**
- DCM correctly loads and parses context files
- LIAL receives the correct persona context based on active_persona_id
- LLM messages include appropriate persona context

**Error Paths to Test:**
- Missing persona definition
- Malformed context files
- Invalid persona ID

### 5.2. User Workflow Scenarios

These scenarios test complete user workflows that exercise multiple components.

#### 5.2.1. Special Command Processing

**Scenario Description:**  
Test that special commands (e.g., /help, /quit, /clear) are correctly handled.

**Components Involved:**  
`UIManager` → `FrameworkController` → `MessageManager` → `UIManager`

**Test Flow:**
1. Initialize FrameworkController with MockUIManager and MessageManager
2. Issue various special commands (/help, /quit, /clear, /debug)
3. Verify each command is correctly processed without LLM interaction
4. Confirm appropriate responses are displayed
5. Check relevant state changes (e.g., conversation cleared)

**Expected Outcomes:**
- Special commands are intercepted by FrameworkController
- LIALManager is not called for special commands
- UIManager displays appropriate responses
- System state is updated correctly (e.g., running=False for /quit)

**Error Paths to Test:**
- Invalid special commands
- Malformed command syntax

#### 5.2.2. Persona Switching Workflow

**Scenario Description:**  
Test the process of switching between Catalyst and Forge personas.

**Components Involved:**  
Full system with mocked LLMAdapter

**Test Flow:**
1. Initialize system with Catalyst as active persona
2. Submit user request that would trigger persona switch recommendation
3. Configure MockLLMAdapter to generate appropriate responses for both personas
4. Confirm proper handling of the switch process
5. Verify active_persona_id updates correctly

**Expected Outcomes:**
- Persona switch request is recognized
- User is prompted for confirmation
- Messages after switch use correct persona
- DCM context is applied correctly for new persona

**Error Paths to Test:**
- User rejection of persona switch
- Switch to invalid persona ID

#### 5.2.3. Multi-turn Conversation with Message Pruning

**Scenario Description:**  
Test a longer conversation that triggers message history pruning.

**Components Involved:**  
`UIManager` → `FrameworkController` → `MessageManager` → `LIALManager` → `UIManager`

**Test Flow:**
1. Configure MessageManager with a low max_messages setting
2. Simulate a multi-turn conversation
3. Verify MessageManager correctly prunes older messages
4. Confirm LIAL receives appropriately pruned message history

**Expected Outcomes:**
- Message history is correctly maintained
- Pruning occurs when threshold is reached
- System messages are preserved as specified in configuration
- LIAL receives proper message sequence

**Error Paths to Test:**
- System message preservation edge cases
- Zero max_messages configuration

### 5.3. Error Handling Scenarios

These scenarios focus on system resilience and error handling capabilities.

#### 5.3.1. LIAL Error Recovery

**Scenario Description:**  
Test system recovery from LLM API failures.

**Components Involved:**  
`FrameworkController` → `LIALManager` → `ErrorHandler` → `UIManager`

**Test Flow:**
1. Configure MockLLMAdapter to throw specific exceptions
2. Submit user input that triggers LLM interaction
3. Verify error is caught and properly handled
4. Confirm appropriate error message is displayed to user
5. Check system continues running despite error

**Expected Outcomes:**
- Errors are caught at component boundaries
- System displays meaningful error messages
- Main loop continues running
- System state remains consistent

**Error Paths to Test:**
- Network timeout
- Authentication error
- Malformed API response
- Rate limiting error

#### 5.3.2. TEPS Error Propagation

**Scenario Description:**  
Test error propagation from tool execution failures.

**Components Involved:**  
`ToolRequestHandler` → `TEPSManager` → `ErrorHandler` → `MessageManager` → `LIALManager`

**Test Flow:**
1. Configure TEPS to simulate specific tool execution failures
2. Trigger a tool request through the system
3. Verify error is caught and formatted properly
4. Confirm error is added to message history
5. Check LLM receives the error information for handling

**Expected Outcomes:**
- Tool execution errors are properly captured
- Error information is formatted as a tool_result message
- Message is added to conversation history
- LLM receives the error information in next interaction
- System remains in a stable state

**Error Paths to Test:**
- File not found
- Permission denied
- Command execution failure
- Timeout during tool execution

#### 5.3.3. Component Initialization Failure

**Scenario Description:**  
Test framework behavior when component initialization fails.

**Components Involved:**  
`FrameworkController` with various failing component managers

**Test Flow:**
1. Configure specific components to fail during initialization
2. Attempt to initialize the framework
3. Verify appropriate error handling and user feedback
4. Check system terminates gracefully

**Expected Outcomes:**
- Initialization failure is detected and reported
- Clear error message indicates the failing component
- System exits gracefully without crashing
- Partial initialization is properly cleaned up

**Error Paths to Test:**
- DCM initialization failure
- LIAL initialization failure
- TEPS initialization failure
- Configuration errors

### 5.4. Full System Integration Scenarios

These scenarios test the complete framework with all components working together.

#### 5.4.1. End-to-End User Session

**Scenario Description:**  
Test a complete user session from initialization to shutdown.

**Components Involved:**  
All components, with mocked external dependencies

**Test Flow:**
1. Start with framework initialization
2. Simulate several user interactions including:
   - Standard text queries
   - Tool requests
   - Special commands
3. End with a /quit command
4. Verify complete system behavior

**Expected Outcomes:**
- Framework initializes correctly
- User interactions are processed correctly
- Tool requests are handled properly
- Special commands work as expected
- System shuts down gracefully

**Error Paths to Test:**
- Unexpected input sequences
- Keyboard interrupts
- Errors during interaction

#### 5.4.2. Configuration Validation

**Scenario Description:**  
Test framework behavior with different configuration scenarios.

**Components Involved:**  
`ConfigurationManager` → `FrameworkController` and all component initializations

**Test Flow:**
1. Prepare various configuration files (minimal, complete, invalid)
2. Initialize framework with each configuration
3. Verify correct behavior for each case

**Expected Outcomes:**
- Valid configurations result in successful initialization
- Invalid configurations produce clear error messages
- Default values are correctly applied for missing optional settings
- Configuration impact on component behavior is as expected

**Error Paths to Test:**
- Missing required settings
- Invalid setting values
- Conflicting settings
- Inaccessible resources

### 5.5. Persona-Specific Scenarios

These scenarios test behavior specific to the Catalyst and Forge personas.

#### 5.5.1. Catalyst Strategic Planning

**Scenario Description:**  
Test interactions specific to the Catalyst persona.

**Components Involved:**  
Full system with active_persona_id set to "catalyst"

**Test Flow:**
1. Initialize system with Catalyst as active persona
2. Submit strategic planning requests
3. Verify appropriate response patterns

**Expected Outcomes:**
- Responses maintain Catalyst persona characteristics
- Strategic content is emphasized over implementation details
- Appropriate formatting and prefixing for Catalyst

**Error Paths to Test:**
- Requests better suited for Forge
- Context confusion scenarios

#### 5.5.2. Forge Implementation with ICERC

**Scenario Description:**  
Test interactions specific to the Forge persona, including ICERC protocol for system operations.

**Components Involved:**  
Full system with active_persona_id set to "forge"

**Test Flow:**
1. Initialize system with Forge as active persona
2. Submit implementation requests requiring system operations
3. Verify ICERC protocol is correctly followed
4. Test user confirmation and tool execution

**Expected Outcomes:**
- Responses maintain Forge persona characteristics
- ICERC protocol is correctly applied for system operations
- Implementation details are appropriately handled
- Tool requests include complete ICERC information

**Error Paths to Test:**
- User rejection of ICERC confirmation
- Requests better suited for Catalyst
- Missing ICERC elements

## 6. Integration Test Implementation Plan

### 6.1. Phase 1: Component Chain Tests
- Implement DCM-LIAL-TEPS chain tests
- Implement Message Manager integration tests
- Implement UI Manager integration tests

### 6.2. Phase 2: Controller and End-to-End Tests
- Implement Controller integration tests
- Implement complete framework integration tests

### 6.3. Phase 3: Error Handling Tests
- Implement error handling and recovery tests

## 7. Deliverables

1. Integration test suite in `/tests/integration/`
2. Test coverage report
3. Documentation of test results and findings
4. Recommendations for framework improvements based on integration testing

## 8. Test Execution and Reporting

### 8.1. Test Execution Strategy

The integration test suite will be executed using a systematic approach to ensure comprehensive testing and reliable results:

#### 8.1.1. Development-Time Testing

During the development of integration tests:

1. **Individual Test Execution**:
   - Run newly developed tests in isolation to verify specific functionality
   - Use `pytest path/to/test_file.py::TestClass::test_method` for targeted testing
   - Focus on one component chain or scenario at a time

2. **Component Group Testing**:
   - Run related tests as a group once individual tests pass
   - Use `pytest path/to/test_directory/` for directory-based test execution
   - Validate interactions between related components

#### 8.1.2. CI/CD Integration

For automated continuous integration:

1. **Test Suite Structure**:
   - Organize tests into logical groups for parallel execution
   - Tag tests with markers for selective execution (e.g., `@pytest.mark.slow`, `@pytest.mark.chain`)

2. **Execution Command**:
   ```bash
   # Run full integration test suite
   pytest tests/integration/ --cov=framework_core

   # Run specific test categories
   pytest tests/integration/ -m "not slow" --cov=framework_core
   ```

3. **Configuration**:
   - Create a `pytest.ini` or `conftest.py` with standardized test settings
   - Configure test timeouts to prevent hanging tests
   - Set up parallel test execution with `pytest-xdist`

#### 8.1.3. Regression Testing Protocol

After code changes:

1. **Pre-Commit Testing**:
   - Run affected integration tests before committing changes
   - Verify no regression in related components

2. **Full Suite Testing**:
   - Run the complete integration test suite after significant changes
   - Ensure changes don't break other parts of the system

3. **Scheduled Full Tests**:
   - Run complete test suite on a regular schedule (e.g., nightly)
   - Include slower, more comprehensive tests in scheduled runs

### 8.2. Test Reporting and Metrics

Integration test results will be documented and analyzed to provide actionable insights:

#### 8.2.1. Coverage Reporting

Test coverage will be measured and reported using:

1. **Coverage Tools**:
   - Use `pytest-cov` for code coverage measurement
   - Generate HTML reports for detailed analysis
   ```bash
   pytest tests/integration/ --cov=framework_core --cov-report=html
   ```

2. **Coverage Metrics**:
   - Line coverage: Percentage of code lines executed during tests
   - Branch coverage: Percentage of code branches (if/else) exercised
   - Component interface coverage: Percentage of component interfaces tested

3. **Coverage Thresholds**:
   - Establish minimum coverage requirements (e.g., 80% line coverage)
   - Configure coverage checks to fail if thresholds aren't met
   ```bash
   pytest tests/integration/ --cov=framework_core --cov-fail-under=80
   ```

#### 8.2.2. Test Result Reporting

Test results will be reported in formats suitable for different stakeholders:

1. **Developer-Focused Reports**:
   - Detailed console output for local development
   - Verbose test logs for debugging failures
   - HTML reports with source code annotation

2. **CI/CD Integration Reports**:
   - JUnit XML output for CI system integration
   - Trend analysis for test stability over time
   - Failure notifications with context

3. **Management Reports**:
   - Summary statistics (pass rate, coverage)
   - Trend analysis of test metrics over time
   - Risk assessment based on coverage gaps

#### 8.2.3. Failure Analysis

Test failures will be systematically analyzed:

1. **Failure Categorization**:
   - Identify failure types (setup issues, assertion failures, timeouts)
   - Track intermittent vs. consistent failures

2. **Root Cause Analysis**:
   - Capture detailed logs and state information for failures
   - Implement test result tagging for common failure patterns

3. **Resolution Tracking**:
   - Link test failures to issue tracking system
   - Verify fixes with previously failed tests

### 8.3. Continuous Improvement Process

The integration testing process will be continuously improved:

1. **Test Quality Reviews**:
   - Regular review of test effectiveness and coverage
   - Identify and refactor brittle or flaky tests
   - Update tests to match evolving system architecture

2. **Test Performance Optimization**:
   - Monitor and optimize test execution time
   - Identify slow tests for potential optimization
   - Implement parallel test execution where possible

3. **Framework Enhancements**:
   - Improve test utilities based on usage patterns
   - Extend mock objects with needed functionality
   - Refine test fixtures for ease of use

## 9. Challenges and Mitigations

| Challenge | Mitigation Strategy |
|-----------|---------------------|
| Mocking complex LLM responses | Create a comprehensive set of mock response templates |
| Testing asynchronous tool execution | Use appropriate test fixtures and timeouts |
| Testing error recovery scenarios | Design specific test cases for each error condition |
| Environment dependencies | Containerize the test environment for consistency |

## 10. Conclusion & Next Steps

### 10.1. Summary

This integration test plan provides a comprehensive strategy for validating the KeystoneAI-Framework's LACA architecture as a cohesive system. The plan addresses several critical aspects:

1. **Component Chain Testing**: Ensures that the core components (DCM, LIAL, TEPS, Controller) work together as designed, with data flowing correctly through defined interfaces.

2. **Scenario-Based Validation**: Verifies that important user workflows, from initialization to tool execution to persona switching, function correctly and reliably.

3. **Resilience Verification**: Confirms that the system handles errors gracefully and maintains stability when components fail or external systems misbehave.

4. **Mocking Strategy**: Provides a consistent approach to simulating external dependencies, ensuring tests are reliable, repeatable, and independent of external services.

5. **Implementation Roadmap**: Outlines a phased approach to developing and executing the integration tests, starting with component chains and progressing to full system integration.

By implementing this test plan, we will create a robust suite of integration tests that detect issues at component boundaries, validate critical workflows, and ensure the framework's stability under various conditions. These tests will complement the existing unit tests to provide comprehensive validation of the framework as both individual components and as a unified system.

### 10.2. Next Steps

To implement this integration test plan, the following actions should be taken in sequence:

1. **Test Environment Setup** (Week 1):
   - Create base test fixtures and utilities
   - Set up the mock LLM adapter
   - Configure the test environment with pytest settings

2. **Phase 1: Component Chain Tests** (Weeks 2-3):
   - Implement DCM-LIAL chain tests
   - Implement LIAL-TEPS chain tests
   - Implement complete DCM-LIAL-TEPS tests

3. **Phase 2: Controller Integration Tests** (Weeks 4-5):
   - Implement initialization tests
   - Implement main loop tests
   - Implement tool request handling tests

4. **Phase 3: End-to-End Tests** (Weeks 6-7):
   - Implement full user workflow tests
   - Implement error handling tests
   - Implement configuration tests

5. **Test Review & Optimization** (Week 8):
   - Review test coverage
   - Optimize test performance
   - Document test results and findings

The implementation team should maintain regular progress updates and conduct reviews after each phase to validate the approach and adjust as needed.

### 10.3. Success Criteria

The integration testing effort will be considered successful when:

1. All specified test cases are implemented and passing
2. Test coverage metrics meet or exceed the 80% line coverage goal
3. All critical user workflows are verified
4. Test execution is stable and repeatable
5. Documentation of the integration testing is complete

This plan provides a foundation for building a reliable, well-tested framework that can be confidently deployed and extended in the future.