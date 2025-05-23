# Framework Interfaces and LLM Requirements (LACA)

**Version:** 1.0
**Date:** 2025-05-13 (Assumed, based on surrounding document dates)
**Authors:** AI Team (Catalyst, Forge)

## 1. Introduction

This document outlines the internal interfaces of the AI-Assisted Framework Version 2, built upon the LLM Agnostic Core Architecture (LACA). It also specifies the minimal requirements for any Large Language Model (LLM) API to be integrated into this framework via the LLM Interaction Abstraction Layer (LIAL). This document replaces the previous `design/05_Claude_Code_Assumptions.md`.

The LACA model is designed to decouple core framework logic from specific LLM provider implementations, allowing for flexibility and easier migration between different LLMs.

## 2. LLM Agnostic Core Architecture (LACA) Overview

The LACA consists of four primary, interconnected components:

1.  **Framework Core Application (`run_framework.py`)**: The central orchestrator. It manages the user interaction loop, initializes all other components, and coordinates the flow of information and actions between them.
2.  **LLM Interaction Abstraction Layer (LIAL)**: The sole component responsible for direct communication with external LLM APIs. It uses specific adapters for different LLM providers.
3.  **Tool Execution & Permission Service (TEPS)**: Manages the execution of system-level tools (e.g., file I/O, bash commands). It is responsible for displaying ICERC (Intent, Command, Expected Outcome, Risk Assessment, Confirmation) information to the user and obtaining explicit permission before any operation.
4.  **Dynamic Context Manager (DCM)**: Parses the `FRAMEWORK_CONTEXT.md` file, loads all referenced foundational documents (personas, standards, workflows), and provides this context to other components, primarily LIAL.

A visual representation of this architecture can be found in `migration_planning_v2/M_Migration_Architecture_v2.md`.

## 3. Key Internal Interfaces & Data Structures

The components interact using well-defined interfaces and data structures.

### 3.1. Framework Core Application Interfaces

*   **Initializes and holds instances of:** DCMManager, LIALManager, TEPSManager, MessageManager, ToolRequestHandler, UIManager.
*   **Manages:**
    *   Conversation history (via MessageManager).
    *   User input/output (via UIManager).
    *   Routing of LLM responses and tool requests.

### 3.2. LIAL Interfaces & Data Structures

*   **`LLMAdapterInterface` (Abstract Base Class in `lial_core.py`):**
    *   `__init__(self, config: Dict, dcm_instance: DynamicContextManager)`: Initializes the adapter with LLM-specific configuration and a DCM instance.
    *   `send_message_sequence(self, messages: List[Message], active_persona_id: Optional[str]) -> LLMResponse`: Sends a sequence of messages to the LLM and returns its response.
*   **Data Structures (defined in `lial_core.py`):**
    *   `Message`:
        *   `role: str` (`"system" | "user" | "assistant" | "tool_result"`)
        *   `content: str`
        *   `tool_call_id: Optional[str]` (for `tool_result` messages)
        *   `tool_name: Optional[str]` (for `tool_result` messages)
    *   `ToolRequest`:
        *   `request_id: str` (Unique ID for the tool call, often generated by LIAL from LLM's tool call ID)
        *   `tool_name: str` (Name of the tool requested by LLM)
        *   `parameters: Dict` (Arguments for the tool, as provided by LLM)
        *   `icerc_full_text: str` (The ICERC pre-brief text, **generated by the LLM (`Forge` persona)** and passed as a parameter within `parameters` or alongside them).
    *   `LLMResponse`:
        *   `conversation: str` (The textual part of the LLM's response)
        *   `tool_request: Optional[ToolRequest]` (If the LLM requests a tool call)
    *   `ToolResult` (Used by TEPS to return results, which LIAL then formats into a `Message` for the LLM):
        *   `request_id: str`
        *   `tool_name: str`
        *   `status: str` (`"success" | "error" | "declined_by_user"`)
        *   `data: Dict` (Output of the tool, e.g., stdout, file content, error message)

### 3.3. TEPS Interfaces & Data Structures

*   **`TEPSEngine` (Class in `teps.py`):**
    *   `execute_tool(self, tool_request: ToolRequest) -> ToolResult`: Primary method to process a tool request.
        *   Displays `tool_request.icerc_full_text` to the user.
        *   Prompts user for [Y/N] confirmation.
        *   If 'Y', executes the tool specified in `tool_request.tool_name` with `tool_request.parameters`.
        *   Returns a `ToolResult`.
*   **Internal Tool Handlers:** TEPS dispatches to internal methods for specific tools (e.g., `_handle_bash`, `_handle_readfile`, `_handle_writefile`). These handlers expect specific keys within the `tool_request.parameters` dictionary.

### 3.4. DCM Interfaces & Data Structures

*   **`DynamicContextManager` (Class in `dcm.py`):**
    *   `__init__(self, context_definition_file_path: str)`: Parses the context definition file.
    *   `get_full_initial_context() -> Dict[str, str]`: Returns all loaded documents.
    *   `get_document_content(doc_id: str) -> Optional[str]`: Retrieves content of a specific document.
    *   `get_persona_definitions() -> Dict[str, str]`: Retrieves all documents marked as personas.
    *   `get_initial_prompt_template() -> Optional[str]`: Retrieves a special initial prompt template.
*   **`FRAMEWORK_CONTEXT.md` Structure:**
    *   Markdown-based file.
    *   Section headers: `## Section Name`
    *   Document references: `doc_id: @./path/to/file.md` (paths relative to `FRAMEWORK_CONTEXT.md`).
    *   Special directive for initial prompt: `# initial_prompt_template: "template text"`

## 4. Minimal LLM API Requirements (for LIAL Adapters)

For an LLM API to be integrated into the framework via a new LIAL adapter, it must support the following core capabilities:

1.  **Context Ingestion:**
    *   Ability to process and utilize a significant volume of initial textual context. This context will include persona definitions, standards, workflows, and other foundational documents managed by DCM.
    *   **Mechanism:** Ideally, a "system prompt" or equivalent that can handle large text inputs (e.g., 200K+ tokens). Alternatively, robust handling of a long series of initial "system" or "user" messages to establish context.

2.  **Instruction Following & Persona Embodiment:**
    *   The LLM must be capable of understanding and adhering to instructions provided within its context, especially regarding persona embodiment (e.g., "You are Catalyst...").
    *   It should maintain the persona characteristics throughout a conversational session.

3.  **Function Calling / Tool Use:**
    *   **Tool Declaration:** The LIAL adapter must be able to declare a predefined set of available tools (functions) to the LLM, including their names, descriptions, and parameter schemas (types, descriptions, required fields).
        *   The framework predefines tools like `executeBashCommand`, `readFile`, `writeFile`.
        *   **Crucially, each tool declared to the LLM must include a parameter for `icerc_full_text` (string type), which the LLM (`Forge` persona) will be prompted to populate.**
    *   **Tool Invocation Request:** When the LLM decides to use a tool, its API response must include a clearly distinguishable, structured representation of the tool call request. This typically includes:
        *   The name of the function/tool to be called.
        *   A dictionary or object of arguments/parameters for the tool, corresponding to the declared schema. The LLM must populate the `icerc_full_text` parameter with the generated ICERC brief.
        *   A unique identifier for the tool call request (if provided by the API, otherwise LIAL can generate one).
    *   **Conversational Text Separation:** The LLM's response should allow for separation of regular conversational text from the structured tool call request.

4.  **Receiving and Processing Tool Execution Results:**
    *   The LLM API must allow the LIAL adapter to send back the results of a tool execution.
    *   This typically involves providing the output/data from the tool (e.g., stdout from a bash command, content of a file, or an error message) in a structured format, often referencing the ID of the original tool call request.
    *   The LLM must be able to process this tool result and use it to inform its subsequent conversational turn or actions.

5.  **Message History / Turn Management:**
    *   The API should support multi-turn conversations by accepting a history of previous messages (user, assistant, system, tool results) to maintain conversational context.

## 5. Configuration System Overview

*   **`framework_config.yaml`**: The primary configuration file for the framework.
    *   Defines which `llm_provider` (LIAL adapter) to use.
    *   Specifies the `api_key_env_var` from which to load the API key.
    *   Provides the path to `context_definition_file` for DCM.
    *   Contains `llm_settings` (nested under provider keys) for LLM-specific parameters (e.g., model name, temperature).
    *   Includes `teps_settings` (e.g., optional command allowlist file).
*   **`FRAMEWORK_CONTEXT.md`**: Managed by DCM, as described in section 3.4. Defines the content and structure of the operational context provided to the LLM.

## 6. TEPS Flow Overview

1.  Framework Core Application receives an `LLMResponse` containing a `ToolRequest` from LIAL.
2.  The `ToolRequest` (including the `icerc_full_text` generated by the LLM) is passed to `teps.execute_tool()`.
3.  TEPS displays the `icerc_full_text` to the user.
4.  TEPS prompts the user for [Y/N] confirmation.
5.  If 'Y', TEPS executes the specified tool using its internal handlers.
6.  TEPS returns a `ToolResult` to the Framework Core Application.
7.  Framework Core Application formats this `ToolResult` into a `Message` (role: `tool_result`) and sends it back to LIAL to inform the LLM of the outcome.

This LACA model and its interfaces aim to create a robust and adaptable framework for AI-assisted development.
