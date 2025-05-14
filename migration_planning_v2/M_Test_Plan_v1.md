# MAIA-Workflow Artifact: M_Test_Plan_v1.md
# Workflow: Framework API Migration: Claude to Gemini 2.5 Pro
# Step: 7 - Testing Strategy for Migrated Framework
# Date: [CURRENT_DATE] - (User to fill)

## 1. Introduction

This document outlines the high-level testing strategy for the AI-Assisted Framework Version 2, which incorporates the LLM Agnostic Core Architecture (LACA) with LIAL, TEPS, and DCM components. The goal is to ensure the refactored framework is robust, functions as designed, and interacts correctly with configured LLMs.

## 2. Overall Testing Objectives

*   Verify the functional correctness of each new core component (Framework Core App, LIAL, TEPS, DCM) individually and in integration.
*   Ensure the framework can successfully load context, manage personas, and orchestrate interaction with a configured LLM (e.g., Gemini 2.5 Pro via its LIAL adapter).
*   Validate that system operations requested by the LLM (via `ToolRequest`) are securely handled by TEPS, including ICERC display and user permission prompting.
*   Confirm that MAIA-Workflows can be executed, demonstrating the end-to-end functionality.
*   Identify and address defects, regressions, and performance issues.

## 3. Testing Levels and Scope

### 3.1. Unit Testing
*   **Objective:** Test individual functions, methods, and classes in isolation.
*   **Scope:**
    *   **DCM (`dcm.py`):** Parsing `FRAMEWORK_CONTEXT.md`, file loading logic, path resolution, getter methods.
    *   **Config Loader (`config_loader.py`):** YAML parsing, key validation, environment variable retrieval for API keys.
    *   **TEPS (`teps.py`):** `execute_tool` dispatch logic, individual tool handlers (`_handle_bash`, `_handle_readfile`, etc.), permission prompting logic (mocked input), error handling.
    *   **LIAL Core (`lial_core.py`):** Abstract interfaces, data structure definitions (if complex).
    *   **LIAL Adapters (e.g., `gemini_adapter.py`):** Message formatting for specific LLM APIs, response parsing (including `ToolRequest` extraction), tool schema declaration, API error mapping.
    *   **Framework Core App (`run_framework.py`):** Utility functions, main loop logic (with LIAL/TEPS/DCM mocked).
*   **Methodology:** Python `unittest` or `pytest`. Extensive use of mocking (`unittest.mock`) for external dependencies (LLM APIs, file system operations, `subprocess`).
*   **Success Criteria:** High code coverage (e.g., >90%) for all new and significantly modified modules. All unit tests passing.

### 3.2. Integration Testing
*   **Objective:** Test the interaction and data flow between integrated LACA components.
*   **Scope & Key Scenarios:**
    1.  **Configuration & Initialization:** `run_framework.py` successfully loads config via `config_loader.py`, initializes DCM, LIAL (with a mock or real adapter), and TEPS.
    2.  **Context Loading:** DCM loads `FRAMEWORK_CONTEXT.md`, LIAL receives context and prepares it for the (mocked) LLM.
    3.  **Initial Prompt Flow:** `run_framework.py` sends initial behavioral prompt via LIAL; LIAL processes a (mocked) LLM text response.
    4.  **Full Tool Call Loop (LIAL <-> TEPS, with Mocked LLM & Mocked System Calls):**
        *   LIAL receives a (mocked) LLM response containing a `ToolRequest` (including `icerc_full_text`).
        *   LIAL correctly passes `ToolRequest` to TEPS.
        *   TEPS displays ICERC, (mocked) user confirms 'Y'.
        *   TEPS "executes" tool (target system call is mocked to return predefined success/failure).
        *   TEPS returns `ToolResult` to LIAL.
        *   LIAL correctly formats and sends `ToolResult` back to the (mocked) LLM.
    5.  **Error Propagation:** Test how errors from TEPS (e.g., tool execution failure, user decline) or LIAL (e.g., LLM API error) are handled and propagated.
*   **Methodology:** `pytest` with fixtures for setting up component instances. Mock the actual LLM API at the LIAL adapter boundary. Mock user console input for TEPS confirmations.
*   **Success Criteria:** All defined integration test scenarios pass. Correct data flow and error handling between components verified.

### 3.3. End-to-End (E2E) / System Testing
*   **Objective:** Test the entire framework operating as a whole, interacting with a live (or highly realistic simulated) LLM API.
*   **Scope & Key Scenarios:**
    1.  **Full User Session Initialization MAIA-Workflow:** (As detailed in previous Test Plan discussion).
    2.  **Basic MAIA-Workflow with File I/O Tool Use:** (e.g., `Forge` writing user input to a file via TEPS).
    3.  **Basic MAIA-Workflow with Bash Command Tool Use:** (e.g., `Forge` listing files in the project directory via TEPS).
    4.  **Persona Adherence:** Verify `Catalyst` and `Forge` (as LLM) generally adhere to their roles and utilize provided context.
    5.  **Failed Tool Execution Handling:** LLM requests a tool call that will fail (e.g., `readFile` on non-existent file, bash command with error). Verify TEPS reports error, and LLM handles it gracefully.
    6.  **Invalid User Input/Commands:** (If framework commands like `/save_state` are implemented).
*   **Methodology:**
    *   Primarily manual execution of test scenarios using the `start_framework.sh` script and interacting via the console.
    *   Requires a configured and working LLM API (e.g., Gemini 2.5 Pro with a valid API key).
    *   (Optional Stretch Goal) Automated E2E tests using console interaction libraries if feasible.
*   **Environment:** Dedicated test project directory, configured `framework_config.yaml` pointing to a live LLM API.
*   **Success Criteria:** All E2E scenarios completed successfully. Framework operates stably. Outputs are as expected. User permissions are correctly enforced by TEPS.

## 4. Test Data Requirements

*   Valid and invalid `framework_config.yaml` files.
*   A representative `FRAMEWORK_CONTEXT.md` with associated dummy local files for import.
*   Predefined user inputs for manual E2E scenarios.
*   Expected console outputs for E2E scenario verification.

## 5. Defect Management

*   Use a simple issue tracker (e.g., GitHub Issues if project is hosted there, or a shared document).
*   Categorize defects by severity and priority.
*   Track defects from discovery through resolution and verification.

## 6. Test Execution Phases (Illustrative)

1.  **Phase 1: Module Development & Unit Testing:** Developers write unit tests alongside module implementation.
2.  **Phase 2: Component Integration & Testing:** Once core modules (DCM, Config, TEPS, LIAL core, one Adapter) are ready, integration tests are run.
3.  **Phase 3: System/E2E Testing:** After successful integration testing, E2E scenarios are executed against a live LLM.
4.  **Phase 4: Regression Testing:** Re-run key E2E and integration tests after significant bug fixes or feature additions.

This test plan provides a foundational strategy. Specific test cases for each scenario will need to be detailed further.
