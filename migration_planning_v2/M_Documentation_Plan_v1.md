# MAIA-Workflow Artifact: M_Documentation_Plan_v1.md
# Workflow: Framework API Migration: Claude to Gemini 2.5 Pro
# Step: 6 - Documentation Update Plan
# Date: [CURRENT_DATE] - (User to fill)

## 1. Introduction

This document outlines the comprehensive plan for updating, finalizing, and maintaining all documentation for the AI-Assisted Framework Version 2. This major update reflects the new LLM Agnostic Core Architecture (LACA), featuring the LIAL, TEPS, and DCM components, and its shift from a Claude Code API-specific implementation.

## 2. Scope of Documentation Updates

All existing framework documentation requires review and significant updates. New documentation will also be created to cover the LACA components and development practices.

## 3. Documentation Update and Creation Plan

### 3.1. Finalize Core Updated Design Documents (from RFI-DOCS-001)
*   **Objective:** Ensure the primary documents reflecting the new architecture are complete, accurate, and clear.
*   **Documents:**
    *   `README.md`
    *   `design/03_End_To_End_System_Flow.md` (V2)
    *   `design/04_Framework_Setup_and_Operational_Notes.md` (V2)
    *   `design/05_Framework_Interfaces_and_LLM_Requirements.md` (New, replaces old `05_Claude_Code_Assumptions.md`)
*   **Tasks:**
    *   Thorough technical review by architects/developers.
    *   Copyediting for clarity, grammar, and style.
    *   Creation/Update of relevant diagrams (e.g., new system overview in `M_Migration_Architecture_v2.md` should be incorporated).
*   **Responsibility (Illustrative):** Lead Developer, `Catalyst` (for review).

### 3.2. Review and Update Foundational Framework Documents
*   **Objective:** Ensure core guiding documents align with LACA operations.
*   **Documents & Key Changes:**
    *   **`personas/catalyst_persona.md` & `personas/forge_persona.md`:**
        *   Remove/rephrase any language implying direct interaction with a specific LLM CLI's native features (e.g., Claude Code CLI).
        *   `Forge` Persona:
            *   Clarify that `Forge` (as an LLM persona) *generates the ICERC pre-brief text* and a *structured `ToolRequest`*.
            *   Emphasize that TEPS (a framework component) handles the display of ICERC, the user Y/N permission prompt, and the actual execution of system operations. `Forge` receives the *result* of the operation via LIAL.
    *   **`standards/ai_assisted_dev_bible.md`:**
        *   **Section 2 (Security Considerations & Review Protocols):**
            *   The "AI System Operation Confirmation Protocol" principles remain valid.
            *   Update any illustrative examples that specifically mentioned the Claude Code CLI's native permission prompt. New examples should show the `Forge` (LLM) -> LIAL -> TEPS -> User Prompt -> TEPS Execution flow.
        *   Review other sections for any minor adjustments needed due to the LACA model.
    *   **`workflows/maia_workflow.md`:**
        *   Review example MAIA-Workflow steps (e.g., Step 3 in the template for User-`Catalyst`-`Forge` interaction).
        *   Ensure descriptions of `Forge`'s actions accurately reflect it requesting tool calls via LIAL/TEPS for system operations, rather than directly executing them.
*   **Responsibility (Illustrative):** `Catalyst`, User (as framework owner).

### 3.3. Create New Developer Guide for LACA
*   **Objective:** Provide essential information for developers working on or extending the Framework V2 core.
*   **Proposed Document Title:** `DEVELOPER_GUIDE_V2.md` (or similar, in a `docs/` directory).
*   **Key Sections:**
    1.  **Architectural Overview:** Detailed explanation of Framework Core App, LIAL, TEPS, DCM, and their interactions (referencing `M_Migration_Architecture_v2.md`).
    2.  **Configuration:**
        *   Detailed guide to `framework_config.yaml` (all options).
        *   Detailed guide to `FRAMEWORK_CONTEXT.md` (syntax, best practices).
    3.  **LIAL Development:**
        *   `LLMAdapterInterface` specification.
        *   Step-by-step guide on "How to Add a New LIAL Adapter" for a different LLM.
        *   Best practices for error handling and message formatting in adapters.
    4.  **TEPS Development:**
        *   `ToolRequest` and `ToolResult` data structures.
        *   How to define and register new tools available to TEPS.
        *   Security considerations for tool handlers.
    5.  **DCM Usage & Extension:** (If applicable beyond parsing `FRAMEWORK_CONTEXT.md`).
    6.  **Logging and Debugging:** Framework's logging strategy and tips for debugging.
    7.  **Testing:** How to write unit and integration tests for new components/adapters.
    8.  **Contribution Guidelines.**
*   **Responsibility (Illustrative):** Lead Developer, `Catalyst` (for structure, review).

### 3.4. Create User Tutorials / Examples (Optional but Recommended)
*   **Objective:** Help new users understand how to use the refactored framework.
*   **Examples:**
    *   A "Getting Started" tutorial that walks through setting up the framework with a (mock or simple) LLM adapter and running a basic MAIA-Workflow.
    *   An example MAIA-Workflow definition that demonstrates a simple tool call (e.g., `Forge` writing "Hello World" to a file via TEPS).
*   **Responsibility (Illustrative):** Developer/User, `Catalyst` (for workflow design).

## 4. Versioning Strategy

*   The refactored framework adopting LACA will be designated **Version 2.0.0**.
*   All core documentation (`README.md`, design documents, personas, Dev Bible, MAIA-WF, Developer Guide) will be versioned in sync with the framework code using Git tags.
*   Significant changes to any document should correspond to a new framework version (patch, minor, or major as appropriate).

## 5. Ongoing Maintenance

*   All future code changes, feature additions, or architectural modifications to the framework **must** include corresponding updates to all relevant documentation.
*   A periodic review (e.g., quarterly or bi-annually) of all documentation should be conducted to ensure accuracy, clarity, and completeness.
*   User feedback on documentation should be actively solicited and addressed.

This plan provides a comprehensive roadmap for aligning all framework documentation with its new V2 architecture.
