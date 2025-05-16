# Framework Setup and Operational Notes: KeystoneAI-Framework with LACA

**Version:** 2.0 (Updated to reflect LLM Agnostic Core Architecture)
**Date:** 2025-05-16
**Designed By:** User & Catalyst

## 1. Introduction

This document provides essential notes for setting up the "KeystoneAI-Framework" repository and understanding key operational aspects of the LLM Agnostic Core Architecture (LACA). This framework enables a structured, standards-based approach to AI-assisted development using the `Catalyst` (AI strategist) and `Forge` (AI implementer) personas through a flexible architecture that can work with various LLM providers.

## 2. Prerequisites

1. **Python Environment:**
   * Users **must** have Python 3.8+ installed on their system.
   * It's recommended to use a virtual environment for the framework.
   * Required Python packages are listed in `requirements.txt`.
2. **Git Installation:**
   * Users must have `git` installed to clone the KeystoneAI-Framework repository.
3. **LLM Provider API Key:**
   * Users must have a valid API key for at least one supported LLM provider (configured in `config.yaml`).
   * The API key should be stored in an environment variable as specified in your `config.yaml`.

## 3. Framework Repository Setup

The KeystoneAI-Framework is distributed as a Git repository containing the Python application, foundational documents, design documentation, and configuration templates.

1. **Clone the Repository:**
   * Obtain the URL for the KeystoneAI-Framework Git repository.
   * Clone the repository to your local system:
     ```bash
     git clone [repository-url] KeystoneAI-Framework
     cd KeystoneAI-Framework
     ```

2. **Directory Structure and Framework Components:**
   * The cloned repository should have the following structure:
     ```
     KeystoneAI-Framework/
     ├── README.md                     # User guide, prerequisites, setup
     ├── requirements.txt              # Python dependencies
     ├── run_framework.py              # Main entry point
     ├── setup.py                      # Installation script
     ├── config/
     │   ├── FRAMEWORK_CONTEXT.md.example  # Template for context definition
     │   └── config.yaml.example       # Template for configuration
     ├── framework_core/               # Core LACA implementation
     │   ├── __init__.py
     │   ├── controller.py             # FrameworkController
     │   ├── dcm.py                    # Dynamic Context Manager
     │   ├── lial_core.py              # LLM Interaction Abstraction Layer
     │   ├── teps.py                   # Tool Execution & Permission Service
     │   ├── adapters/                 # LLM provider-specific adapters
     │   │   ├── __init__.py
     │   │   └── gemini_adapter.py     # Example provider adapter
     │   └── ...
     ├── assets/
     │   ├── personas/
     │   │   ├── catalyst_persona.md   # Defines the Catalyst persona
     │   │   └── forge_persona.md      # Defines the Forge persona
     │   ├── standards/
     │   │   └── ai_assisted_dev_bible.md # The AI-Assisted Dev Bible
     │   ├── workflows/
     │   │   └── maia_workflow.md      # The MAIA-Workflow framework definition
     │   └── design/                   # Design artifacts
     │       ├── 01_User_Session_Initialization_MAIA_Workflow.md
     │       ├── 02_Project_State_JSON_Structure.md
     │       ├── 03_End_To_End_System_Flow.md
     │       ├── 04_Framework_Setup_and_Operational_Notes.md (This file)
     │       └── 05_Framework_Interfaces_and_LLM_Requirements.md
     └── example-project/              # Template project for users to copy
         ├── config/
         │   ├── FRAMEWORK_CONTEXT.md
         │   └── config.yaml
         └── assets/
             └── ...
     ```
   * The `framework_core/` directory contains the Python implementation of the LACA architecture.
   * The `assets/` directory contains foundational documents referenced by the framework.

3. **Configuring the Framework:**
   * **Create a Configuration File:**
     * Copy `config/config.yaml.example` to a location of your choice, for example:
       ```bash
       cp config/config.yaml.example my-project-config.yaml
       ```
     * Edit the configuration file to include your LLM provider settings, API key environment variable name, and other preferences.
   * **Create a Framework Context Definition:**
     * Copy `config/FRAMEWORK_CONTEXT.md.example` to a location of your choice, for example:
       ```bash
       cp config/FRAMEWORK_CONTEXT.md.example my-project-context.md
       ```
     * Edit this file to reference the foundational documents and set up the initial prompting for the LLM.

4. **Installing Dependencies:**
   * Set up a Python virtual environment (recommended):
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
   * Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

5. **Optional: Creating a Wrapper Script**
   * You may create a simple wrapper script (`start_framework.sh` or similar) to simplify launching the framework:
     ```bash
     #!/bin/bash
     
     # Configure environment variables for your LLM provider
     export GEMINI_API_KEY=your_api_key
     # or export ANTHROPIC_API_KEY=your_api_key
     # or export OPENAI_API_KEY=your_api_key
     
     # Run the framework with your config
     python run_framework.py --config my-project-config.yaml
     ```
   * Make the script executable: `chmod +x start_framework.sh`

## 4. Running the Framework

1. **Set Environment Variables:**
   * Set the environment variable for your LLM provider API key as specified in your config file, for example:
     ```bash
     export GEMINI_API_KEY=your_api_key
     ```

2. **Run the Framework:**
   * Execute the main framework script with your configuration:
     ```bash
     python run_framework.py --config path/to/your/config.yaml
     ```
   * Or use your wrapper script if you created one:
     ```bash
     ./start_framework.sh
     ```

3. **Session Initialization:**
   * The `FrameworkController` initializes core components:
     * `DCM` loads content from `FRAMEWORK_CONTEXT.md` and its referenced documents.
     * `LIAL` is initialized with the configured LLM provider adapter.
     * `TEPS` is initialized to handle tool requests and their permissions.
   * The LLM (through LIAL) receives the initial context and embodies the `Catalyst` persona.
   * The LLM (as `Catalyst`) initiates the "User Session Initialization" MAIA-Workflow.

## 5. Key Operational Notes

1. **ICERC Protocol Implementation:**
   * The AI-Assisted Dev Bible (Section 2) mandates the "AI System Operation Confirmation Protocol." The `Forge` persona implements this via the **ICERC** (Intent, Command, Expected Outcome, Risk Assessment, Confirmation Request) protocol.
   * **Crucial Interaction Flow:** When `Forge` (as the LLM) needs to execute a system command (bash) or perform a file modification (write/edit):
     1. `(Forge)` will create a ToolRequest with the appropriate tool (e.g., `executeBashCommand`, `writeFile`) and include a full ICERC pre-brief in its request:
        * Stating its **Intent**.
        * Showing the exact **Command(s)**.
        * Describing the **Expected Outcome**.
        * Providing a **Risk Assessment**.
     2. This ToolRequest is sent via LIAL to the FrameworkController, which passes it to TEPS.
     3. TEPS displays the ICERC pre-brief to the User and asks for [Y/N] confirmation.
     4. The User makes their decision based on the detailed ICERC explanation.
     5. If confirmed, TEPS executes the requested operation and returns the result to the LLM via FrameworkController and LIAL.
   * The "Dry-Run" option for ICERC is managed conversationally by `Forge`. If a User desires a dry run after seeing the ICERC pre-brief, they should decline TEPS's execution prompt and then explicitly ask `Forge` to describe or simulate a dry run.

2. **Project Directory and `maia_project_state.json`:**
   * During the "User Session Initialization" MAIA-Workflow, a specific `Project_Directory_Path` will be established.
   * All project-specific artifacts (RFIs, code, `Forge`'s reports, etc.) will be stored within this directory.
   * Session state (including the status of active MAIA-Workflows) is saved to a `maia_project_state.json` file in the root of this `Project_Directory_Path`. This file is managed by `Catalyst` (directing `Forge` for writes via TEPS).
   * The `FrameworkController` manages the current working directory of the Python process through TEPS (using `os.chdir`).

3. **Persona Switching:**
   * Persona switches between `(Catalyst)` and `(Forge)` are explicitly proposed by the currently active LLM persona and require User confirmation [Y/N] before the switch occurs.
   * The `FrameworkController` manages the active persona, updating the internal state and informing LIAL of the change for subsequent LLM interactions.
   * All LLM responses are prefixed with `(Catalyst)` or `(Forge)` for clarity.

4. **User Responsibility for Version Control:**
   * The framework facilitates the creation of artifacts in the `Project_Directory_Path`. The User is responsible for initializing and managing version control (e.g., `git`) for this directory.

5. **Context Management:**
   * Context is managed by the `DCM` component, which parses `FRAMEWORK_CONTEXT.md` and all referenced documents.
   * The `FRAMEWORK_CONTEXT.md` file contains references to foundational documents (personas, standards, workflows) and can include an initial prompt template.
   * The structure of `FRAMEWORK_CONTEXT.md` is:
     * Markdown-based file.
     * Section headers: `## Section Name`
     * Document references: `doc_id: @./path/to/file.md` (paths relative to `FRAMEWORK_CONTEXT.md`).
     * Special directive for initial prompt: `# initial_prompt_template: "template text"`
   * Project-specific contexts can be created by having different `FRAMEWORK_CONTEXT.md` files for different projects.

These notes should provide a solid foundation for setting up and effectively using the KeystoneAI-Framework with its LACA architecture.