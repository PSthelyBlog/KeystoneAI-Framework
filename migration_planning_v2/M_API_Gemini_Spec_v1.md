# MAIA-Workflow Artifact: M_API_Gemini_Spec_v1.md
# Workflow: Framework API Migration: Claude to Gemini 2.5 Pro
# Step: 1 - Gemini 2.5 Pro API - Functional Definition & Requirements
# Date: [CURRENT_DATE] - (User to fill)

## 1. Introduction

This document outlines the functional definition, requirements, and proposed solutions for utilizing a hypothetical Gemini 2.5 Pro API (or similar advanced LLM API) to support the AI-Assisted Framework. It also details the decision to evolve the framework towards an LLM Agnostic Core Architecture (LACA) featuring a LLM Interaction Abstraction Layer (LIAL), Tool Execution & Permission Service (TEPS), and Dynamic Context Manager (DCM).

## 2. Key LLM API Functional Requirements for the Framework

The framework, in its refactored LACA model, requires the underlying LLM API (interfaced via LIAL) to support the following core capabilities:

### 2.1. Context & Memory System
*   **Requirement:** Ability to ingest and utilize large volumes of initial context (foundational documents like personas, Dev Bible, workflows).
*   **Proposed Solution (for LIAL adapter to target):**
    *   **Ideal:** An API endpoint for setting/updating session-level "system context" or "background documents" with unique IDs (e.g., `upsert_document(doc_id="dev_bible", content="...")`). The LLM can then be instructed to refer to these `doc_id`s.
    *   **Sufficient:** A very large system prompt capability (e.g., 200K+ tokens) where the DCM, via LIAL, can provide concatenated foundational documents.
*   **Internal Framework Handling:** The DCM will manage a `FRAMEWORK_CONTEXT.md` (or similar structured file) to define and load these documents. The LIAL adapter will be responsible for formatting and sending this context to the LLM according to the chosen LLM's specific mechanism.

### 2.2. Persona Embodiment & Management
*   **Requirement:** The LLM must be able to embody and maintain distinct AI personas (`Catalyst`, `Forge`) based on detailed textual descriptions provided in its context. It must also support switching between these personas during a session based on framework-driven instructions.
*   **Proposed Solution (for LIAL adapter to target):**
    *   **Initial Embodiment:** Part of the initial system prompt or first user message after context loading (e.g., "You are to embody the `Catalyst` persona defined in 'persona_catalyst_doc'...").
    *   **Persona Switching:** Managed through explicit instructions in user/assistant messages, mediated by the LIAL. The LIAL ensures the LLM is reminded of the active persona's definition.
    *   **Ideal (LLM API feature):** An API parameter to set/update the "active_persona_id" or "role_definition_document_id" for the LLM's responses could simplify this for the LIAL.

### 2.3. Tool Use / Function Calling
*   **Requirement:** The LLM must support a mechanism to request the execution of predefined external tools (e.g., for bash commands, file I/O) by providing the tool name and its parameters in a structured format.
*   **Proposed Solution (for LIAL adapter to target):**
    *   **Essential:** Robust support for the LLM API to:
        1.  Be informed of available tools/functions and their schemas (name, description, parameters) by the LIAL during session setup or per request.
        2.  Respond with a structured JSON object (or similar) when it intends to call a function, specifying the function name and arguments. This response must clearly distinguish the function call request from regular conversational text.
    *   **Internal Framework Handling:** The LIAL will declare a set of tools (e.g., `executeBashCommand`, `readFile`, `writeFile`) to the LLM. When the LLM requests a tool call, LIAL parses this and forwards it to TEPS.
    *   **Critical for ICERC:** The LLM (`Forge` persona) must be promptable to include the full ICERC pre-brief text as a string parameter within the arguments of the function call it requests (e.g., `parameters: {"command": "mkdir ...", "icerc_full_text": "Intent: ..., Command: ..., ..."}`).

### 2.4. Receiving Tool Execution Results
*   **Requirement:** After an external tool (managed by TEPS) is executed, the LLM API must allow the framework (via LIAL) to send back the results of that tool execution (e.g., stdout/stderr, file content, success/error status). The LLM should then use this result to inform its next conversational turn or subsequent actions.
*   **Proposed Solution (for LIAL adapter to target):**
    *   **Essential:** The LLM API must support a message type or mechanism for providing the output/result of a previously requested function call. This often involves referencing the ID of the original function call request.

## 3. LLM Agnostic Core Architecture (LACA) Decision

To support robust migration and future flexibility, the framework will be refactored to include:

*   **LLM Interaction Abstraction Layer (LIAL):** The sole component communicating with LLM APIs. Contains LLM-specific adapters. Translates generic internal requests to specific API calls and standardizes responses.
*   **Tool Execution & Permission Service (TEPS):** Manages all tool execution (bash, file I/O) and user permission flows (displaying ICERC from LLM, prompting Y/N, executing command, returning results).
*   **Dynamic Context Manager (DCM):** Parses `FRAMEWORK_CONTEXT.md`, loads foundational documents, and provides context to LIAL.

This architecture decouples core framework logic from specific LLM APIs, making the LLM provider a configurable choice.

## 4. Conclusion

The AI-Assisted Framework V2 will target LLM APIs that meet these core functional requirements, primarily robust context handling and a well-defined function calling mechanism. The LACA model will ensure that specific LLM API features related to direct system operation or permissioning are not required, as these responsibilities are internalized within the TEPS module. This approach maximizes flexibility and security.
