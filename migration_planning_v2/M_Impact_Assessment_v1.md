# MAIA-Workflow Artifact: M_Impact_Assessment_v1.md
# Workflow: Framework API Migration: Claude to Gemini 2.5 Pro
# Step: 2 - Impact Analysis on AI-Assisted Framework
# Date: [CURRENT_DATE] - (User to fill)

## 1. Introduction

This document details the impact assessment of migrating the AI-Assisted Framework from its original Claude Code API-centric design to the new LLM Agnostic Core Architecture (LACA), featuring the LLM Interaction Abstraction Layer (LIAL), Tool Execution & Permission Service (TEPS), and Dynamic Context Manager (DCM).

## 2. Impact on Existing Framework Components

The introduction of LACA necessitates significant changes or replacements for several key components of the original framework:

### 2.1. `start.sh` Script
*   **Current Reliance:** Launches `claude` CLI, passes initial prompt, relies on `claude` CLI for `CLAUDE.md` processing.
*   **Impact:** **Major Rewrite/Replacement.**
    *   The new script (e.g., `start_framework.sh`) will launch a new Framework Core Application (e.g., Python-based).
    *   It will no longer interact directly with an LLM CLI.
    *   Responsibilities shift to initializing the Framework Core Application and passing configuration.

### 2.2. `CLAUDE.md` (Primary Context File)
*   **Current Reliance:** Claude Code CLI's memory system, `@import` directives.
*   **Impact:** **Replaced/Evolved.**
    *   Will be replaced by `FRAMEWORK_CONTEXT.md` (or similar structured file like YAML).
    *   Parsing and document loading will be handled by the new DCM module.
    *   The `@import` syntax might be retained or replaced by a more structured definition within the new context file.

### 2.3. Persona Definitions (`catalyst_persona.md`, `forge_persona.md`)
*   **Current Reliance:** Loaded by `CLAUDE.md` into Claude's context.
*   **Impact:**
    *   **Content:** Largely unchanged conceptually.
    *   **Loading:** Handled by DCM and passed to the LLM via LIAL.
    *   **`Forge` Persona ICERC:** The description of `Forge`'s ICERC process needs rephrasing. `Forge` (as LLM) will still *generate the ICERC pre-brief text*, but this text will be passed as part of a structured `ToolRequest` to LIAL, then to TEPS. TEPS will handle the user-facing permission prompt and execution.

### 2.4. Standards & Workflows (`ai_assisted_dev_bible.md`, `maia_workflow.md`)
*   **Current Reliance:** Loaded by `CLAUDE.md` into Claude's context.
*   **Impact:**
    *   **Content:** Largely unchanged in principles.
    *   **Loading:** Handled by DCM.
    *   **Dev Bible Sec 2 (AI System Operation Confirmation Protocol):** Illustrative examples mentioning direct Claude CLI prompts will need updating to reflect the new LIAL/TEPS flow (LLM generates ICERC text -> LIAL -> TEPS -> User Prompt -> TEPS executes).

### 2.5. Design Documents (`design/` directory)
*   **`01_User_Session_Initialization_MAIA_Workflow.md`:**
    *   **Impact:** Conceptual steps remain, but implementation details of system operations (`mkdir`, `cd`, `pwd`, `readFile`) must reflect the `Forge` (LLM) -> LIAL -> TEPS flow.
*   **`02_Project_State_JSON_Structure.md`:**
    *   **Impact:** Minor. `framework_version_info` field will need to accommodate new LACA component versions (LIAL, TEPS, DCM, Core App).
*   **`03_End_To_End_System_Flow.md`:**
    *   **Impact:** **Significant Rewrite.** Must describe the new flow involving `start_framework.sh`, Framework Core App, LIAL, TEPS, DCM, and generic LLM interaction.
*   **`04_Framework_Setup_and_Operational_Notes.md`:**
    *   **Impact:** **Significant Rewrite.** Prerequisites, setup instructions, `CLAUDE.md` sections, `start.sh` sections, and ICERC explanation must all be updated.
*   **`05_Claude_Code_Assumptions.md`:**
    *   **Impact:** **Obsolete.** To be replaced by a new document (`design/05_Framework_Interfaces_and_LLM_Requirements.md`) detailing LACA internal interfaces and minimal LLM API requirements for LIAL adaptation.

### 2.6. `README.md`
*   **Impact:** **Significant Rewrite.** Overview, Prerequisites, Quick Start, What to Expect, Key Operational Principles, and Customization sections all need to reflect the new LACA model.

## 3. New Components to Be Developed

The LACA model requires the creation of entirely new software components:

*   **Framework Core Application:** The main executable/script orchestrating LIAL, TEPS, and DCM.
*   **LLM Interaction Abstraction Layer (LIAL):** Core module and LLM-specific adapters (e.g., `GeminiAdapter`, `ClaudeAdapter`).
*   **Tool Execution & Permission Service (TEPS):** Module for executing system operations and managing user permissions.
*   **Dynamic Context Manager (DCM):** Module for parsing `FRAMEWORK_CONTEXT.md` and loading documents.
*   **Configuration System:** For `framework_config.yaml` parsing and management.
*   **New Context Definition File (`FRAMEWORK_CONTEXT.md` or equivalent).**

## 4. Summary of Impact

The migration to the LACA model is a substantial architectural refactor. While the core intellectual property of the framework (personas, Dev Bible principles, MAIA-Workflow methodology) is preserved, the underlying implementation for LLM interaction, context management, and system operations will be completely new. Documentation will require extensive updates. The primary benefit is a more modular, secure, testable, and LLM-agnostic framework.
