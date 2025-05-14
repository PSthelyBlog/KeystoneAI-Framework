# MAIA-Workflow Artifact: M_Migration_Architecture_v2.md
# Workflow: Framework API Migration: Claude to Gemini 2.5 Pro
# Step: 3 - Migration Strategy & Architectural Design
# Date: [CURRENT_DATE] - (User to fill)

## 1. Introduction

This document details the refined architectural design for the AI-Assisted Framework Version 2. This design implements the LLM Agnostic Core Architecture (LACA), enabling the framework to interact with various Large Language Models (LLMs) through a configurable abstraction layer. The core components are the Framework Core Application, LLM Interaction Abstraction Layer (LIAL), Tool Execution & Permission Service (TEPS), and Dynamic Context Manager (DCM).

## 2. System Overview & Component Interaction

The framework operates as a local application (e.g., Python-based) launched by `start_framework.sh`.

```
+---------------------------+      +--------------------------------+      +------------------------+
| User (Console Interface)  |<---->|   Framework Core Application   |<---->|          LIAL          |
+---------------------------+      | (run_framework.py)             |      | (LLM Interaction Abs.) |-----> (LLM API, e.g., Gemini)
                                   |  - Main Interaction Loop       |      |  - LLM Adapters        |
                                   |  - Orchestrates LIAL,TEPS,DCM  |      |  - Msg Formatting      |
                                   +-----------+--------+-----------+      +------------------------+
                                               |        |
                                               |        | (ToolRequest)
                                   (Context)   |        | (ToolResult)
                                               V        V
                                   +-----------+--------+-----------+
                                   |          TEPS          |      |           DCM          |
                                   | (Tool Exec & Permission) |      | (Dynamic Context Mgr)  |
                                   |  - ICERC Display         |      |  - Parses FRAMEWORK_   |
                                   |  - User Y/N Prompt       |<---->|    CONTEXT.md          |
                                   |  - Executes Sys Ops      |      |  - Loads Docs          |
                                   +--------------------------+      +------------------------+
                                          |
                                          V (Sys Calls: bash, file I/O)
                                   +--------------------------+
                                   |   Local File System/OS   |
                                   +--------------------------+
```

## 3. Core Component Designs

### 3.1. Framework Core Application (`run_framework.py`)
*   **Responsibilities:**
    *   Entry point of the application.
    *   Parses command-line arguments (e.g., config file path).
    *   Loads `framework_config.yaml` via the Configuration System.
    *   Initializes DCM, LIAL (with the configured LLM adapter), and TEPS.
    *   Manages the main user interaction loop:
        1.  Sends initial behavioral prompt to LLM via LIAL.
        2.  Receives `LLMResponse` from LIAL.
        3.  Displays conversational part to user.
        4.  If `ToolRequest` is present in `LLMResponse`:
            *   Passes `ToolRequest` to TEPS.
            *   Receives `ToolResult` from TEPS.
            *   Sends `ToolResult` back to LLM via LIAL (as a `Message`).
            *   Loops to get next LLM response.
        5.  Else (no tool request):
            *   Reads user's text input.
            *   Handles framework-specific commands (e.g., `/quit`).
            *   Sends user text as a `Message` to LLM via LIAL.
    *   Handles basic error logging and graceful shutdown.

### 3.2. LLM Interaction Abstraction Layer (LIAL)
*   **`lial_core.py`:**
    *   Defines `LLMAdapterInterface` (Abstract Base Class) with methods like:
        *   `__init__(self, config: Dict, dcm_instance: DynamicContextManager)`
        *   `send_message_sequence(self, messages: List[Message], active_persona_id: Optional[str]) -> LLMResponse`
    *   Defines common data structures:
        *   `Message = {"role": "system" | "user" | "assistant" | "tool_result", "content": str, "tool_call_id": Optional[str], "tool_name": Optional[str]}`
        *   `ToolRequest = {"request_id": str, "tool_name": str, "parameters": Dict, "icerc_full_text": str}` (Note: `icerc_full_text` is populated by LLM (`Forge`) as a parameter).
        *   `LLMResponse = {"conversation": str, "tool_request": Optional[ToolRequest]}`
*   **LLM Adapters (e.g., `gemini_adapter.py`, `claude_adapter.py`):**
    *   Implement `LLMAdapterInterface`.
    *   Handle LLM-specific authentication and API client initialization.
    *   Translate internal `Message` list to the LLM's specific message/prompt format.
    *   Declare available tools/functions to the LLM using its specific mechanism (e.g., Gemini's `tools` and `function_declarations`).
    *   Make API calls to the LLM.
    *   Parse LLM API responses, extracting conversational text and translating any LLM function call requests into the internal `ToolRequest` format.
    *   Format `ToolResult` data into the structure expected by the LLM when reporting tool execution outcomes.

### 3.3. Tool Execution & Permission Service (TEPS)
*   **`teps.py`:**
    *   Provides `execute_tool(self, tool_request: ToolRequest) -> ToolResult` method.
    *   Receives `ToolRequest` from LIAL.
    *   Displays `tool_request.parameters.get("icerc_full_text")` to the user console.
    *   Prompts the user for [Y/N] confirmation based on the `tool_request.tool_name` and `tool_request.parameters`.
    *   If confirmed 'Y':
        *   Dispatches to internal handlers for specific tools (e.g., `_handle_bash`, `_handle_readfile`, `_handle_writefile`).
        *   Executes the system operation using standard Python libraries (`subprocess`, `os`, file I/O).
        *   Captures results (stdout, stderr, exit code, file content, success/error status).
    *   Returns `ToolResult = {"request_id": str, "tool_name": str, "status": "success" | "error" | "declined_by_user", "data": Dict}`.
    *   May manage a per-project command allowlist (optional feature).

### 3.4. Dynamic Context Manager (DCM)
*   **`dcm.py`:**
    *   `__init__(self, context_definition_file_path: str)`: Parses `FRAMEWORK_CONTEXT.md`.
    *   Parses lines like `doc_id: @./path/to/file.md`, resolving paths relative to `FRAMEWORK_CONTEXT.md`.
    *   Loads content of specified files into an internal dictionary (`doc_id -> content`).
    *   Provides methods like:
        *   `get_full_initial_context() -> Dict[str, str]`
        *   `get_document_content(doc_id: str) -> Optional[str]`
        *   `get_persona_definitions() -> Dict[str, str]`
        *   `get_initial_prompt_template() -> Optional[str]` (from a special comment in `FRAMEWORK_CONTEXT.md`)

## 4. Configuration Files

### 4.1. `framework_config.yaml`
*   **Purpose:** Main configuration for the Framework Core Application.
*   **Structure Example:**
    ```yaml
    llm_provider: "gemini_2_5_pro"  # Identifies which LIAL adapter to use
    api_key_env_var: "GEMINI_API_KEY" # Environment variable name for the API key
    context_definition_file: "./config/FRAMEWORK_CONTEXT.md" # Path to context definition

    llm_settings: # Optional, LLM-specific settings passed to the adapter
      gemini_2_5_pro:
        model_name: "gemini-1.5-pro-latest"
      # claude_3_opus:
      #   model_name: "claude-3-opus-20240229"

    teps_settings: # Optional
      allowlist_file: ".project_teps_allowlist.json"
    ```
*   Handled by `config_loader.py`.

### 4.2. `FRAMEWORK_CONTEXT.md`
*   **Purpose:** Defines all foundational documents to be loaded into the LLM's context.
*   **Structure Example (Markdown with section headers and key: @path syntax):**
    ```markdown
    # Framework Context Definition v1.0

    ## Personas
    persona_catalyst: @../personas/catalyst_persona.md
    persona_forge: @../personas/forge_persona.md

    ## Standards
    standard_dev_bible: @../standards/ai_assisted_dev_bible.md
    # ... etc.
    ```
    (Paths are relative to this file, assuming it's in `config/` and personas are in `../personas/`)

## 5. Data Flow for a Tool Call (Example: `Forge` runs `mkdir`)

1.  **LLM (`Forge` persona):** Generates conversational text including ICERC pre-brief. Also generates a `functionCall` request for `executeBashCommand` with parameters: `command="mkdir ..."`, `working_directory="..."`, `icerc_full_text="Intent: ..., Command: ..., ..."`.
2.  **LIAL (`GeminiAdapter`):** Receives LLM API response. Parses conversational text and translates `functionCall` into an internal `ToolRequest` object, ensuring `icerc_full_text` is part of it.
3.  **Framework Core App:** Receives `LLMResponse` from LIAL. Displays conversational text. Sees `ToolRequest` is present.
4.  **Framework Core App to TEPS:** Calls `teps.execute_tool(tool_request)`.
5.  **TEPS:**
    *   Displays `tool_request.parameters.get("icerc_full_text")`.
    *   Prompts user: `Execute command: mkdir ...? [Y/N]`.
    *   User responds 'Y'.
    *   TEPS executes `mkdir` via `subprocess.run`.
    *   TEPS creates `ToolResult` (e.g., `{"status": "success", "data": {"stdout": ..., "exit_code": 0}}`).
6.  **TEPS to Framework Core App:** Returns `ToolResult`.
7.  **Framework Core App to LIAL:** Creates a `Message(role="tool_result", ...)` containing the `ToolResult` data and sends it via `lial.send_message_sequence()`.
8.  **LIAL (`GeminiAdapter`):** Formats the tool result message for the Gemini API and sends it.
9.  **LLM (`Forge` persona):** Receives tool result, processes it, and generates next conversational turn.

This architecture provides a modular and extensible foundation for the AI-Assisted Framework.
