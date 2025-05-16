# End-to-End User Experience and System Flow: KeystoneAI-Framework

**Version:** 2.0
**Date:** 2025-05-16
**Designed By:** User & Catalyst

## 0. Introduction

This document outlines the complete end-to-end user experience and system flow for the KeystoneAI-Framework, which integrates `Catalyst` (AI strategist), `Forge` (AI implementer), The AI-Assisted Dev Bible (standards), and the MAIA-Workflow (methodology) within an LLM Agnostic Core Architecture (LACA). The framework is implemented as a Python application with core components: `FrameworkController`, `DCM` (Dynamic Context Manager), `LIAL` (LLM Interaction Abstraction Layer), and `TEPS` (Tool Execution & Permission Service).

## 1. Phase 0: One-Time User Setup (External to Interactive Session)

1. **Setup Python Environment (Prerequisite):**
   * The User must have Python 3.8+ installed on their system.
   * It's recommended to use a virtual environment for the framework installation.
2. **Acquire KeystoneAI-Framework Repository:**
   * The User clones the "KeystoneAI-Framework" Git repository from its source (e.g., GitHub).
   * This repository contains:
     * Framework Python application code (`framework_core/` directory).
     * Foundational documents (`assets/personas/catalyst_persona.md`, `assets/personas/forge_persona.md`, `assets/standards/ai_assisted_dev_bible.md`, `assets/workflows/maia_workflow.md`).
     * A primary `FRAMEWORK_CONTEXT.md.example` file (to be configured by the user).
     * Configuration file templates (`config/config.yaml.example`).
     * A comprehensive `README.md` detailing prerequisites and usage instructions for the framework.
   * Basic installation steps:
     ```bash
     git clone [repository-url] KeystoneAI-Framework
     cd KeystoneAI-Framework
     pip install -r requirements.txt
     ```

## 2. Phase 1: Starting a New Interactive Session

1. **Navigate to Framework Directory:**
   * The User opens their terminal and navigates (`cd`) into the directory where they cloned the "KeystoneAI-Framework" repository.
2. **Configure Environment:**
   * The User configures their LLM provider API keys as environment variables (specific variable names are defined in `config.yaml`).
   * The User creates/customizes `config.yaml` from the provided template.
   * The User creates/customizes `FRAMEWORK_CONTEXT.md` from the provided example, ensuring references to foundational documents are correct.
3. **Run the Framework Application:**
   * The User executes the command `python run_framework.py --config path/to/config.yaml` (or uses a wrapper script if one has been created).
4. **Automatic Framework Initialization:**
   * The `FrameworkController` initializes the core components:
     * `DCM` loads and parses `FRAMEWORK_CONTEXT.md` and all referenced documents.
     * `LIAL` is initialized with the configured LLM provider adapter.
     * `TEPS` is initialized to handle tool requests and user permissions.
   * `LIAL` sends the initial prompt (defined in `FRAMEWORK_CONTEXT.md` or `config.yaml`) to the LLM.
   * The LLM processes the context and adopts the `Catalyst` persona.
5. **`Catalyst` Initiates User Session:**
   * The LLM, now acting as `(Catalyst)`, begins the interactive terminal session with the User by launching the "User Session Initialization" MAIA-Workflow.

## 3. Phase 2: "User Session Initialization" MAIA-Workflow

This workflow is orchestrated by `(Catalyst)` to set up the specific project environment for the current session.

* **Step 1: Welcome and Project Path Acquisition:**
  * `(Catalyst)` welcomes the User, provides a brief overview of the framework's operational principles (personas, Dev Bible, MAIA-WF, ICERC for system commands).
  * `(Catalyst)` prompts the User to provide the absolute path to their target project directory.
  * User provides the path.
* **Step 2: Project Environment Setup & State Handling:**
  * `(Catalyst)` explains the need to verify/create the directory and set the Current Working Directory (CWD), proposing a switch to the `Forge` persona for these system operations. User confirms the switch [Y/N].
  * If approved, the `FrameworkController` updates the active persona to `Forge`:
    * **Directory Operations:** `(Forge)` checks if the `User_Provided_Project_Path` exists.
      * If it exists, `(Forge)` formulates a ToolRequest with the `executeBashCommand` tool to change to and verify the directory. This request includes an ICERC pre-brief (Intent, Command (`cd`, `pwd`), Expected Outcome, Risk Assessment) that is passed to TEPS. TEPS displays the ICERC information and prompts the User for [Y/N] confirmation before executing the command.
      * If it doesn't exist, `(Forge)` formulates a ToolRequest to create the directory (`mkdir -p`), again with an ICERC pre-brief. TEPS displays this to the User for confirmation. If successful, `(Forge)` then issues ToolRequests for changing into and verifying the new directory (`cd`, `pwd`), each with its own ICERC text and User confirmation via TEPS.
    * The framework process's effective CWD is now the `Project_Directory_Path`.
    * **State File Handling:** `(Forge)` formulates a ToolRequest with the `readFile` tool to read `[Project_Directory_Path]/maia_project_state.json`.
      * If `maia_project_state.json` is found and read successfully, `(Forge)` displays its content and proposes switching back to `(Catalyst)` for processing. User confirms switch [Y/N].
        * The `FrameworkController` updates the active persona to `Catalyst`.
        * `(Catalyst)` parses and validates the JSON content.
        * If valid, `(Catalyst)` restores the session context (active MAIA-Workflow, current step, variables, etc.) and informs the User they are ready to resume the saved MAIA-Workflow.
        * If invalid/corrupt, `(Catalyst)` discusses recovery options with the User (e.g., start fresh, attempt to show raw content for external fixing).
      * If `maia_project_state.json` is not found (or unreadable), `(Forge)` informs the User it will be a new project session and proposes switching back to `(Catalyst)`. User confirms switch [Y/N].
        * The `FrameworkController` updates the active persona to `Catalyst`.
        * `(Catalyst)` confirms a fresh project setup and informs the User they are ready to start a new MAIA-Workflow.
  * The "User Session Initialization" MAIA-Workflow is now complete. `(Catalyst)` is ready to proceed with project-specific work.

## 4. Phase 3: Executing Project-Specific MAIA-Workflows

Once the session is initialized, `(Catalyst)` collaborates with the User to execute project-specific tasks using MAIA-Workflows.

1. **Workflow Orchestration:**
   * `(Catalyst)` helps the User define a new MAIA-Workflow or select an existing MAIA-Workflow template relevant to the project's goals (e.g., "Feature Development," "Bug Triage," "Documentation Generation").
   * `(Catalyst)` guides the execution of the chosen MAIA-Workflow step-by-step, managing inputs, AI actions, User actions, and outputs for each step.
2. **Persona Interaction & Handoffs:**
   * All LLM responses are prefixed with `(Catalyst)` or `(Forge)` for clarity.
   * When `(Catalyst)` needs `Forge` for implementation (e.g., after drafting an RFI):
     * `(Catalyst)` first ensures the RFI (or other necessary input for `Forge`) is saved to a file within the `Project_Directory_Path`. This save operation is done by `(Catalyst)` directing `(Forge)` (via a persona switch confirmed by the user) to perform the file write. `(Forge)` formulates a ToolRequest with the `writeFile` tool, including a full ICERC pre-brief. TEPS displays this pre-brief and asks the User for confirmation.
     * `(Catalyst)` then proposes a switch to the `(Forge)` persona to process the RFI/task. User confirms switch [Y/N].
   * `(Forge)` then takes over:
     * It creates a ToolRequest to read the RFI (or other inputs) from the specified file path.
     * It may produce an "Implementation Pre-Brief," saving it to a file via a ToolRequest (with ICERC and TEPS permission prompt).
     * It implements code, scripts, or other artifacts, saving them to files via ToolRequests (with ICERC and TEPS permission prompts).
     * It runs tests (potentially involving more ICERC-confirmed ToolRequests if tests involve system interaction).
     * It generates a "Task Completion Report," saving it to a file via a ToolRequest (with ICERC and TEPS permission prompt).
   * `(Forge)` then proposes switching back to `(Catalyst)` for review and next steps. User confirms switch [Y/N].
   * This collaborative loop between `(Catalyst)`, `(Forge)`, and the User continues throughout the MAIA-Workflow.
3. **AI-Assisted Dev Bible Adherence:**
   * Both `(Catalyst)` and `(Forge)` operate with the internalized AI-Assisted Dev Bible as their guiding standard.
   * `(Catalyst)` explicitly references relevant Dev Bible sections in RFIs and strategic discussions.
   * `(Forge)` confirms its understanding and applies these standards meticulously, especially:
     * **ICERC Protocol:** For every system-altering bash command or file modification, `(Forge)` first provides a full ICERC pre-brief (Intent, Command, Expected Outcome, Risk Assessment) as part of its ToolRequest. TEPS then displays this information and requires the User's [Y/N] confirmation before executing the command.
     * Security, testing, documentation, and version control practices as per the Dev Bible.
4. **Artifact Management:**
   * All significant artifacts (RFIs, `Forge`'s reports, source code, test suites, `maia_project_state.json`, documentation) are stored as files within the `Project_Directory_Path` (potentially in subdirectories like `rfis/`, `src/`, `tests/`, `forge_reports/`, `docs/`).
   * File creation and modification operations initiated by `(Forge)` (or by `(Catalyst)` directing `(Forge)`) are always subject to the ICERC pre-brief by `(Forge)` and subsequent User confirmation via TEPS.
   * The User is responsible for managing version control (e.g., using `git`) for the artifacts within the `Project_Directory_Path`, committing changes as appropriate with Dev Bible-compliant messages (e.g., `[AI-GEN]`, `[AI-ASSIST]`).
5. **MAIA-Workflow Completion & State Export:**
   * When a project-specific MAIA-Workflow is completed, or at any logical point where the User wishes to save progress:
     * `(Catalyst)` initiates the "Project State Consolidation & Export" step (as defined in the general MAIA-Workflow framework document, Section 8).
     * This involves `(Catalyst)` (directing `(Forge)` for the file write) creating or updating the `maia_project_state.json` file in the root of the `Project_Directory_Path`. `(Forge)` formulates a ToolRequest with the `writeFile` tool, including an ICERC pre-brief. TEPS displays this information to the User for confirmation.
     * The `maia_project_state.json` file will contain the current state of the active MAIA-Workflow (name, step, variables), artifact manifest, etc., as per its defined structure.

## 5. Phase 4: Ending the Interactive Session

1. **User Decision:** The User decides to end the current interactive session.
2. **State Preservation:** `(Catalyst)` should have ideally recently saved the project state to `maia_project_state.json` if significant progress was made or if a MAIA-Workflow was completed. The User can also explicitly request `(Catalyst)` to save the state before exiting.
3. **Exit:** The User can type `/quit` (or another designated command processed by `FrameworkController`) to exit the application. Alternatively, they can close the terminal window or use Ctrl+C to terminate the Python process.
4. **Persistence:** The project state (including the `maia_project_state.json` file and all other generated artifacts) remains in the User's local `Project_Directory_Path`, ready for the next session.

This flow ensures a structured, secure, and standards-compliant approach to AI-assisted development using the `Catalyst` and `Forge` personas within the KeystoneAI-Framework's LLM Agnostic Core Architecture.