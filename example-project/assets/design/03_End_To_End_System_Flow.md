# End-to-End User Experience and System Flow: AI-Assisted Framework with Claude Code

**Version:** 1.0
**Date:** [Current Date - User to fill when saving]
**Designed By:** User & Catalyst

## 0. Introduction

This document outlines the complete end-to-end user experience and system flow for the AI-Assisted Framework, which integrates `Catalyst` (AI strategist), `Forge` (AI implementer), The AI-Assisted Dev Bible (standards), and the MAIA-Workflow (methodology) within the Claude Code API environment, accessed via the `claude` command-line interface (CLI).

## 1. Phase 0: One-Time User Setup (External to Interactive Session)

1.  **Install Claude Code CLI (Prerequisite):**
    *   The User must first install the `claude` CLI tool globally on their system. Instructions for this are provided by Anthropic (or will be clearly linked in our Framework's `README.md`). This is a one-time setup per system.
2.  **Acquire AI-Assisted Framework Repository:**
    *   The User clones the "AI-Assisted Framework" Git repository from its source (e.g., GitHub).
    *   This repository contains:
        *   Foundational documents (`personas/catalyst_persona.md`, `personas/forge_persona.md`, `standards/ai_assisted_dev_bible.md`, `workflows/maia_workflow.md`).
        *   A primary `CLAUDE.md` file in the root directory, configured to:
            *   Import the above foundational documents using the `@path/to/import` syntax.
            *   Provide an initial instruction to Claude to embody the `Catalyst` persona upon session start.
        *   A comprehensive `README.md` detailing prerequisites (like installing the `claude` CLI) and usage instructions for the framework.
    *   No `npm install` step is required for the framework repository itself.

## 2. Phase 1: Starting a New Interactive Session

1.  **Navigate to Framework/Project Directory:**
    *   The User opens their terminal and navigates (`cd`) into the directory where they cloned the "AI-Assisted Framework" repository, or into a specific project directory that has been set up to use the framework's `CLAUDE.md` (e.g., by having its own `CLAUDE.md` that imports the framework's main `CLAUDE.md`, or by being a subdirectory where Claude Code's upward recursive lookup will find the framework's `CLAUDE.md`).
2.  **Run Claude Code CLI:**
    *   The User executes the command `claude` (or its alias, e.g., `c`).
3.  **Automatic Framework Initialization by Claude Code CLI:**
    *   The `claude` CLI automatically discovers and processes the `CLAUDE.md` file(s) based on its lookup rules (current directory, then parent directories).
    *   It loads the content of the primary `CLAUDE.md` and, through its `@import` directives, loads the full text of the foundational documents (`catalyst_persona.md`, `forge_persona.md`, `ai_assisted_dev_bible.md`, `maia_workflow.md`) into Claude's initial context.
    *   Claude processes this initial context and follows the instruction within the primary `CLAUDE.md` to embody the `Catalyst` persona.
4.  **`Catalyst` Initiates User Session:**
    *   Claude, now fully initialized and acting as `(Catalyst)`, begins the interactive terminal session with the User by launching the "User Session Initialization" MAIA-Workflow.

## 3. Phase 2: "User Session Initialization" MAIA-Workflow

This workflow is orchestrated by `(Catalyst)` to set up the specific project environment for the current session.

*   **Step 1: Welcome and Project Path Acquisition:**
    *   `(Catalyst)` welcomes the User, provides a brief overview of the framework's operational principles (personas, Dev Bible, MAIA-WF, ICERC for system commands).
    *   `(Catalyst)` prompts the User to provide the absolute path to their target project directory.
    *   User provides the path.
*   **Step 2: Project Environment Setup & State Handling:**
    *   `(Catalyst)` explains the need to verify/create the directory and set the Current Working Directory (CWD), proposing a switch to the `Forge` persona for these system operations. User confirms the switch [Y/N].
    *   If approved, `(Forge)` takes over:
        *   **Directory Operations:** `(Forge)` checks if the `User_Provided_Project_Path` exists.
            *   If it exists, `(Forge)` presents an ICERC pre-brief (Intent, Command (`cd`, `pwd`), Expected Outcome, Risk Assessment) for changing to and verifying the directory. User then confirms/denies the actual commands via Claude Code's native Y/N permission prompts.
            *   If it doesn't exist, `(Forge)` presents an ICERC pre-brief for creating the directory (`mkdir -p`), followed by user confirmation via Claude Code's prompt. If successful, `(Forge)` then presents an ICERC pre-brief for changing into and verifying the new directory (`cd`, `pwd`), again with User confirmation via Claude Code's prompts.
        *   The `claude` CLI's effective CWD is now the `Project_Directory_Path`.
        *   **State File Handling:** `(Forge)` attempts to read `[Project_Directory_Path]/maia_project_state.json` (this read operation itself does not require Claude Code's permission prompt).
            *   If `maia_project_state.json` is found and read successfully, `(Forge)` displays its content and proposes switching back to `(Catalyst)` for processing. User confirms switch [Y/N].
                *   `(Catalyst)` parses and validates the JSON content.
                *   If valid, `(Catalyst)` restores the session context (active MAIA-Workflow, current step, variables, etc.) and informs the User they are ready to resume the saved MAIA-Workflow.
                *   If invalid/corrupt, `(Catalyst)` discusses recovery options with the User (e.g., start fresh, attempt to show raw content for external fixing).
            *   If `maia_project_state.json` is not found (or unreadable), `(Forge)` informs the User it will be a new project session and proposes switching back to `(Catalyst)`. User confirms switch [Y/N].
                *   `(Catalyst)` confirms a fresh project setup and informs the User they are ready to start a new MAIA-Workflow.
    *   The "User Session Initialization" MAIA-Workflow is now complete. `(Catalyst)` is ready to proceed with project-specific work.

## 4. Phase 3: Executing Project-Specific MAIA-Workflows

Once the session is initialized, `(Catalyst)` collaborates with the User to execute project-specific tasks using MAIA-Workflows.

1.  **Workflow Orchestration:**
    *   `(Catalyst)` helps the User define a new MAIA-Workflow or select an existing MAIA-Workflow template relevant to the project's goals (e.g., "Feature Development," "Bug Triage," "Documentation Generation").
    *   `(Catalyst)` guides the execution of the chosen MAIA-Workflow step-by-step, managing inputs, AI actions, User actions, and outputs for each step.
2.  **Persona Interaction & Handoffs:**
    *   All AI responses are prefixed with `(Catalyst)` or `(Forge)` for clarity.
    *   When `(Catalyst)` needs `Forge` for implementation (e.g., after drafting an RFI):
        *   `(Catalyst)` first ensures the RFI (or other necessary input for `Forge`) is saved to a file within the `Project_Directory_Path`. This save operation is done by `(Catalyst)` directing `(Forge)` (via a quick persona switch confirmed by the user) to perform the file write, which involves `(Forge)` presenting an ICERC pre-brief and the User confirming the action via Claude Code's native permission prompt.
        *   `(Catalyst)` then proposes a switch to the `(Forge)` persona to process the RFI/task. User confirms switch [Y/N].
    *   `(Forge)` then takes over:
        *   It reads the RFI (or other inputs) from the specified file path.
        *   It may produce an "Implementation Pre-Brief," saving it to a file (via ICERC and Claude Code's permission prompt).
        *   It implements code, scripts, or other artifacts, saving them to files (via ICERC and Claude Code's permission prompt).
        *   It runs tests (potentially involving more ICERC-confirmed commands if tests involve system interaction).
        *   It generates a "Task Completion Report," saving it to a file (via ICERC and Claude Code's permission prompt).
    *   `(Forge)` then proposes switching back to `(Catalyst)` for review and next steps. User confirms switch [Y/N].
    *   This collaborative loop between `(Catalyst)`, `(Forge)`, and the User continues throughout the MAIA-Workflow.
3.  **AI-Assisted Dev Bible Adherence:**
    *   Both `(Catalyst)` and `(Forge)` operate with the internalized AI-Assisted Dev Bible as their guiding standard.
    *   `(Catalyst)` explicitly references relevant Dev Bible sections in RFIs and strategic discussions.
    *   `(Forge)` confirms its understanding and applies these standards meticulously, especially:
        *   **ICERC Protocol:** For every system-altering bash command or file modification, `(Forge)` first provides a full ICERC pre-brief (Intent, Command, Expected Outcome, Risk Assessment) in its conversational output. Then, it signals the command to Claude Code, which triggers Claude Code's native Y/N permission prompt for that specific command.
        *   Security, testing, documentation, and version control practices as per the Dev Bible.
4.  **Artifact Management:**
    *   All significant artifacts (RFIs, `Forge`'s reports, source code, test suites, `maia_project_state.json`, documentation) are stored as files within the `Project_Directory_Path` (potentially in subdirectories like `rfis/`, `src/`, `tests/`, `forge_reports/`, `docs/`).
    *   File creation and modification operations initiated by `(Forge)` (or by `(Catalyst)` directing `(Forge)`) are always subject to the ICERC pre-brief by `(Forge)` and subsequent User confirmation via Claude Code's native permission prompt.
    *   The User is responsible for managing version control (e.g., using `git`) for the artifacts within the `Project_Directory_Path`, committing changes as appropriate with Dev Bible-compliant messages (e.g., `[AI-GEN]`, `[AI-ASSIST]`).
5.  **MAIA-Workflow Completion & State Export:**
    *   When a project-specific MAIA-Workflow is completed, or at any logical point where the User wishes to save progress:
        *   `(Catalyst)` initiates the "Project State Consolidation & Export" step (as defined in the general MAIA-Workflow framework document, Section 8).
        *   This involves `(Catalyst)` (directing `(Forge)` for the file write) creating or updating the `maia_project_state.json` file in the root of the `Project_Directory_Path`. This save operation includes an ICERC pre-brief from `(Forge)` and User confirmation via Claude Code's native prompt.
        *   The `maia_project_state.json` file will contain the current state of the active MAIA-Workflow (name, step, variables), artifact manifest, etc., as per its defined structure.

## 5. Phase 4: Ending the Interactive Session

1.  **User Decision:** The User decides to end the current interactive session.
2.  **State Preservation:** `(Catalyst)` should have ideally recently saved the project state to `maia_project_state.json` if significant progress was made or if a MAIA-Workflow was completed. The User can also explicitly request `(Catalyst)` to save the state before exiting.
3.  **Exit:** The User can close the terminal window or use any standard method to terminate the `claude` CLI application.
4.  **Persistence:** The project state (including the `maia_project_state.json` file and all other generated artifacts) remains in the User's local `Project_Directory_Path`, ready for the next session.

This flow ensures a structured, secure, and standards-compliant approach to AI-assisted development using the `Catalyst` and `Forge` personas within the Claude Code environment.
