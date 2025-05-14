# Framework Setup and Operational Notes: AI-Assisted Framework with Claude Code

**Version:** 1.1 (Updated to reflect `start.sh` initialization)
**Date:** [Current Date - User to fill when saving]
**Designed By:** User & Catalyst

## 1. Introduction

This document provides essential notes for setting up the "AI-Assisted Framework" repository and understanding key operational aspects when using it with the Claude Code command-line interface (`claude` CLI). This framework enables a structured, standards-based approach to AI-assisted development using the `Catalyst` (AI strategist) and `Forge` (AI implementer) personas.

## 2. Prerequisites

1.  **Claude Code CLI Installation:**
    *   Users **must** have the `claude` CLI tool (provided by Anthropic) installed and configured on their system. This is the primary interface for interacting with the framework.
    *   Refer to the official Anthropic documentation for instructions on installing and authenticating the `claude` CLI: [https://docs.anthropic.com/en/docs/claude-code/getting-started](https://docs.anthropic.com/en/docs/claude-code/getting-started)
    *   This framework does **not** install the `claude` CLI itself.
2.  **Git Installation:**
    *   Users must have `git` installed to clone the AI-Assisted Framework repository.
3.  **Bash-compatible Shell:**
    *   A Bash-compatible shell is required to run the `start.sh` script. This is standard on Linux and macOS. Windows users may use Windows Subsystem for Linux (WSL) or Git Bash.

## 3. Framework Repository Setup

The AI-Assisted Framework is distributed as a Git repository containing foundational documents, design documentation, and configuration for the `claude` CLI.

1.  **Clone the Repository:**
    *   Obtain the URL for the AI-Assisted Framework Git repository (e.g., `https://github.com/PSthelyBlog/ai_assisted_framework_claude.git`).
    *   Clone the repository to your local system:
        ```bash
        git clone https://github.com/PSthelyBlog/ai_assisted_framework_claude.git
        cd ai_assisted_framework_claude
        ```

2.  **Directory Structure and Foundational Documents:**
    *   The cloned repository should have the following structure:
        ```
        ai_assisted_framework_claude/
        ├── CLAUDE.md                 # Primary Claude Code memory file (loads context)
        ├── README.md                 # User guide, prerequisites, setup
        ├── start.sh                  # Script to launch the framework with initial prompt
        ├── personas/
        │   ├── catalyst_persona.md   # Defines the Catalyst persona
        │   └── forge_persona.md      # Defines the Forge persona
        ├── standards/
        │   └── ai_assisted_dev_bible.md # The AI-Assisted Dev Bible
        ├── workflows/
        │   └── maia_workflow.md      # The MAIA-Workflow framework definition
        └── design/                     # Design artifacts (also loaded by CLAUDE.md)
            ├── 01_User_Session_Initialization_MAIA_Workflow.md
            ├── 02_Project_State_JSON_Structure.md
            ├── 03_End_To_End_System_Flow.md
            ├── 04_Framework_Setup_and_Operational_Notes.md (This file)
            └── 05_Claude_Code_Assumptions.md
        ```
    *   Ensure paths in `CLAUDE.md`'s `@import` statements correctly reference these files.

3.  **Primary `CLAUDE.md` Configuration (Context Loading):**
    *   The `CLAUDE.md` file in the root of the `ai_assisted_framework_claude` directory is used by the `claude` CLI to load extensive context into Claude's memory.
    *   It should contain `@import` statements for all foundational documents (personas, standards, workflows) and the design documents.
    *   **Example `CLAUDE.md` content (illustrative, verify against actual file):**
        ```markdown
        # AI-Assisted Framework Context Load
        
        ## Core Persona Definitions
        - Catalyst Persona (Strategic AI Lead): @./personas/catalyst_persona.md
        - Forge Persona (Implementation AI Specialist): @./personas/forge_persona.md
        
        ## Governing Standards and Workflow Methodology
        - The AI-Assisted Dev Bible (Comprehensive Standards): @./standards/ai_assisted_dev_bible.md
        - MAIA-Workflow Framework (Structured Process): @./workflows/maia_workflow.md

        ## Design Documents (For Framework Self-Awareness)
        - User Session Initialization Workflow: @./design/01_User_Session_Initialization_MAIA_Workflow.md
        - Project State JSON Structure: @./design/02_Project_State_JSON_Structure.md
        - End-to-End System Flow: @./design/03_End_To_End_System_Flow.md
        - Framework Setup and Operational Notes: @./design/04_Framework_Setup_and_Operational_Notes.md
        - Claude Code Assumptions: @./design/05_Claude_Code_Assumptions.md
        ```
    *   **Note:** The `CLAUDE.md` file itself no longer needs to contain the "Initial Operating Instruction for Claude," as this is now handled by `start.sh`.

4.  **`start.sh` Script (Initial Prompting & Launch):**
    *   The `start.sh` script is responsible for launching the `claude` CLI and providing it with the crucial initial behavioral prompt.
    *   Ensure `start.sh` is executable (`chmod +x start.sh`).
    *   **Conceptual content of `start.sh`:**
        ```bash
        #!/bin/bash
        
        # This script launches the AI-Assisted Framework using the Claude Code CLI.
        # It provides the essential initial prompt to instruct Claude on its starting persona and task.
        
        INITIAL_PROMPT="You are to embody the \`Catalyst\` persona as defined in your loaded context (catalyst_persona.md) from the very start of this session. Your immediate goal upon starting is to initiate the 'User Session Initialization' MAIA-Workflow with the User (the definition of which is available to you via your loaded context for 01_User_Session_Initialization_MAIA_Workflow.md). All your actions and those of the \`Forge\` persona (when active) must rigorously adhere to the principles and protocols outlined in The AI-Assisted Dev Bible."
        
        # Launch claude with the initial prompt.
        # The exact mechanism for passing an initial prompt depends on the claude CLI's capabilities.
        # Example: Assuming claude can take a prompt via an argument:
        # claude --initial-prompt "$INITIAL_PROMPT"
        
        # Example: Or if it reads from stdin for an initial prompt:
        # echo "$INITIAL_PROMPT" | claude --read-prompt-from-stdin
        
        # Replace the line below with the actual command supported by your 'claude' CLI version
        # for passing an initial prompt. If no direct way, the script might just run 'claude'
        # and the user might need to paste the initial prompt manually (less ideal).
        claude <<EOF
        $INITIAL_PROMPT
        EOF
        # The above here-document approach is one way to pipe multi-line input if claude accepts it.
        # Test thoroughly to find the most reliable method for your claude CLI version.
        ```
    *   **Action Required:** The user/developer must ensure the `claude` command within `start.sh` correctly passes the `INITIAL_PROMPT` to the CLI. The example uses a here-document, but other methods like `--initial-prompt "..."` or piping might be appropriate depending on the `claude` CLI's features. This needs to be verified.

5.  **No `npm install` Required for the Framework:**
    *   The framework itself does not have Node.js dependencies requiring `npm install`.

## 4. Running the Framework

1.  **Navigate to the Framework Directory:**
    *   Open your terminal and `cd` into the root of the cloned `ai_assisted_framework_claude` directory.
        ```bash
        cd path/to/ai_assisted_framework_claude
        ```
2.  **Ensure `start.sh` is Executable (One-time):**
    ```bash
    chmod +x start.sh
    ```
3.  **Execute the `start.sh` Script:**
    ```bash
    ./start.sh
    ```
4.  **Session Initialization:**
    *   The `start.sh` script launches `claude`.
    *   The `claude` CLI loads context from `CLAUDE.md` and its imports.
    *   The `start.sh` script provides the initial prompt.
    *   Claude will start as `(Catalyst)` and initiate the "User Session Initialization" MAIA-Workflow.

## 5. Key Operational Notes

(This section remains largely the same as previously defined, emphasizing ICERC, project directory, persona switching, version control, and Claude Code's memory system. No changes are needed here based on the `start.sh` modification, as those principles apply once the session is running.)

1.  **ICERC Protocol Implementation by `Forge`:**
    *   The AI-Assisted Dev Bible (Section 2) mandates the "AI System Operation Confirmation Protocol." The `Forge` persona implements this via the **ICERC** (Intent, Command, Expected Outcome, Risk Assessment, Confirmation Request) protocol.
    *   **Crucial Interaction Flow:** When `Forge` (as Claude) needs to execute a system command (bash) or perform a file modification (write/edit):
        1.  `(Forge)` will first **conversationally output** the full ICERC pre-brief:
            *   Stating its **Intent**.
            *   Showing the exact **Command(s)**.
            *   Describing the **Expected Outcome**.
            *   Providing a **Risk Assessment**.
        2.  Only *after* `Forge` has provided this textual ICERC pre-brief will it signal to the underlying Claude Code mechanism to attempt the action.
        3.  Claude Code's native permission system will then display its own prompt (typically showing the command again) and ask the User for "Yes" / "No" approval.
        4.  The User makes their decision based on both `Forge`'s detailed ICERC explanation and Claude Code's direct command prompt.
    *   The "Dry-Run" option for ICERC is managed conversationally by `Forge`. If a User desires a dry run after seeing the ICERC pre-brief, they should decline Claude Code's execution prompt and then explicitly ask `Forge` to describe or simulate a dry run.

2.  **Project Directory and `maia_project_state.json`:**
    *   During the "User Session Initialization" MAIA-Workflow, a specific `Project_Directory_Path` will be established.
    *   All project-specific artifacts (RFIs, code, `Forge`'s reports, etc.) will be stored within this directory.
    *   Session state (including the status of active MAIA-Workflows) is saved to a `maia_project_state.json` file in the root of this `Project_Directory_Path`. This file is managed by `Catalyst` (directing `Forge` for writes via ICERC).

3.  **Persona Switching:**
    *   Persona switches between `(Catalyst)` and `(Forge)` are explicitly proposed by the currently active AI persona and require User confirmation [Y/N] before the switch occurs.
    *   All AI responses are prefixed with `(Catalyst)` or `(Forge)` for clarity.

4.  **User Responsibility for Version Control:**
    *   The framework facilitates the creation of artifacts in the `Project_Directory_Path`. The User is responsible for initializing and managing version control (e.g., `git`) for this directory.

5.  **Claude Code Memory System (`CLAUDE.md`):**
    *   Users can further customize their experience by using Claude Code's hierarchical `CLAUDE.md` memory system:
        *   **Project-specific `CLAUDE.md`:** A `CLAUDE.md` within the `Project_Directory_Path` can contain instructions or context specific to that project (e.g., coding standards, API keys for that project). It can even `@import` the main framework's `CLAUDE.md` if desired to ensure framework principles are also loaded.
        *   **User-global `CLAUDE.md`:** A `~/.claude/CLAUDE.md` can store personal preferences applicable across all projects.
    *   Refer to Claude Code documentation for details on memory lookup order and best practices.

These notes should provide a solid foundation for setting up and effectively using the AI-Assisted Framework with the Claude Code CLI, incorporating the `start.sh` script for reliable initialization.
