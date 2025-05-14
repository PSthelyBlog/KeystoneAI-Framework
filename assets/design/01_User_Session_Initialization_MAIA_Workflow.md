# MAIA-Workflow: User Session Initialization

**Version:** 1.0
**Date:** [Current Date - User to fill when saving]
**Designed By:** User & Catalyst

**Overall Goal:** To smoothly onboard the User into a new or existing project within the "AI-Assisted Framework" environment, establishing a controlled project directory, loading any existing project state, and preparing for task execution.

**Pre-conditions:**
*   The "AI-Assisted Framework" application (i.e., the `claude` CLI) has been started by the User from within the AI-Assisted Framework Git repository (or a directory where its `CLAUDE.md` is discoverable).
*   Claude has been initialized by the `claude` CLI with the foundational documents (`catalyst_persona.md`, `forge_persona.md`, `ai_assisted_dev_bible.md`, `maia_workflow.md`) via the primary `CLAUDE.md` and its imports.
*   Claude is currently embodying the `Catalyst` persona as per initial instructions in the primary `CLAUDE.md`.

---
## Step 1: Welcome and Project Path Acquisition

*   **Step Goal:** To welcome the User, briefly explain the session's operational context, and acquire the desired project directory path.
*   **Execution Mode:** Standard
*   **Primary Human Role:** `ProjectInitiator`, `PathProvider`
*   **Primary AI Assistant Role(s):** `Catalyst` (as Claude)
*   **Inputs:** None (start of a new interactive session after `claude` CLI launch and initial persona embodiment).
*   **AI Actions (`Catalyst` as Claude):**
    1.  `(Catalyst)`: "Welcome to the AI-Assisted Framework environment. I am `Catalyst`, your AI strategist and team lead. I operate based on The AI-Assisted Dev Bible and will guide our work using the MAIA-Workflow. `Forge` is available for implementation tasks under my direction. All system operations will be confirmed via the ICERC protocol as implemented by `Forge` before Claude Code's native permission prompt."
    2.  `(Catalyst)`: "To begin, please provide the absolute path to your project directory. If the directory does not exist, we can create it. This directory will be the central location for all our work and artifacts for this session."
*   **User Actions:**
    1.  Acknowledge `Catalyst`'s welcome.
    2.  Provide the absolute path to the desired project directory (e.g., `/home/user/my_ai_project`).
*   **Outputs:**
    *   `User_Provided_Project_Path` (string): The absolute path string provided by the User.
*   **Completion Criteria:**
    *   User has provided a project directory path string.

---
## Step 2: Project Environment Setup & State Handling

*   **Step Goal:** To verify/create the project directory, set it as the current working directory for the `claude` CLI session, and attempt to load any existing `maia_project_state.json` file to resume a previous session or initialize a new one.
*   **Execution Mode:** Standard
*   **Primary Human Role:** `OperationConfirmer`, `DecisionMaker` (if state loading issues arise)
*   **Primary AI Assistant Role(s):** `Catalyst` (as Claude, directing `Forge` for system operations and state processing)
*   **Inputs:**
    *   `User_Provided_Project_Path` (from Step 1).
*   **AI Actions (`Catalyst` as Claude, directing `Forge` where necessary):**
    1.  `(Catalyst)`: "Thank you. I will now ask `Forge` to verify or create the project directory at `[User_Provided_Project_Path]` and set it as our current working directory. `Forge` will first present the full ICERC context (Intent, Command, Expected Outcome, Risk Assessment) for any necessary system commands, after which Claude Code's native permission prompt will appear for your final [Y/N] approval."
    2.  **(Handoff to `Forge` for directory operations - User confirms switch)**
        *   `(Catalyst)`: "To proceed with setting up the project directory, I recommend switching to the `Forge` persona. `Forge` will handle the necessary system commands. Do you approve this switch to the `Forge` persona? [Y/N]"
        *   **User:** Responds [Y/N].
        *   If User responds **Y**:
            *   `(Forge)`: "Understood. I am now `Forge`. I will check if `[User_Provided_Project_Path]` exists. If not, I will propose creating it. If it exists, I will propose setting it as the current working directory."
            *   **(Sub-Step 2.1: Directory Verification/Creation - `Forge` leads)**
                *   `Forge` (as Claude) first determines if the directory `[User_Provided_Project_Path]` exists (e.g., by preparing to use `ls` or a similar check, which doesn't require permission if just for listing).
                    *   **If directory exists:**
                        *   `(Forge)`: "The directory `[User_Provided_Project_Path]` already exists. I will now prepare the commands to change into this directory and confirm our location.
                            **ICERC Pre-Brief:**
                            *   **Intent:** To set the provided existing directory as the active project's working directory for this session and verify the change.
                            *   **Commands:**
                                1.  `cd "[User_Provided_Project_Path]"`
                                2.  `pwd`
                            *   **Expected Outcome:** The shell's current working directory will change to `[User_Provided_Project_Path]`, and `pwd` will output this new path.
                            *   **Risk Assessment:** Low. If the path is incorrect or permissions are insufficient, `cd` will fail. No data is modified by these commands.
                            Please prepare to confirm these commands via Claude Code's permission prompt."
                        *   (`Forge` then signals to Claude Code to execute `cd "[User_Provided_Project_Path]"`. Claude Code's native Y/N permission prompt appears. User confirms.)
                        *   (`Forge` then signals to Claude Code to execute `pwd`. Claude Code's native Y/N permission prompt appears for `pwd` if it's configured to require it, or it executes if not. `pwd` output is captured.)
                        *   `Project_Directory_Path` (internal context variable) is set to the confirmed path.
                    *   **If directory does NOT exist:**
                        *   `(Forge)`: "The directory `[User_Provided_Project_Path]` does not exist. I will now prepare the command to create it.
                            **ICERC Pre-Brief:**
                            *   **Intent:** To create the new project directory as specified by the user.
                            *   **Command:** `mkdir -p "[User_Provided_Project_Path]"`
                            *   **Expected Outcome:** The directory `[User_Provided_Project_Path]` (and any necessary parent directories) will be created.
                            *   **Risk Assessment:** Low. Creates a new directory. If the path is invalid (e.g., due to permissions in a parent segment), the command may fail.
                            Please prepare to confirm this command via Claude Code's permission prompt."
                        *   (`Forge` then signals to Claude Code to execute `mkdir -p "[User_Provided_Project_Path]"`. Claude Code's native Y/N permission prompt appears. User confirms.)
                        *   If successful, `Forge` proceeds: "The directory has been created. I will now prepare commands to change into this directory and confirm our location.
                            **ICERC Pre-Brief:**
                            *   **Intent:** To set the newly created directory as the active project's working directory and verify the change.
                            *   **Commands:**
                                1.  `cd "[User_Provided_Project_Path]"`
                                2.  `pwd`
                            *   **Expected Outcome:** The shell's current working directory will change to `[User_Provided_Project_Path]`, and `pwd` will output this new path.
                            *   **Risk Assessment:** Low.
                            Please prepare to confirm these commands via Claude Code's permission prompt."
                        *   (`Forge` signals for `cd` and `pwd` execution as above, with User confirmations via Claude Code's prompts.)
                        *   `Project_Directory_Path` (internal context variable) is set to the confirmed path.
                *   Upon successful CWD change:
                    *   `(Forge)`: "The project directory is now set to `[Confirmed_Absolute_Path]`. The current working directory is confirmed by the output of `pwd`."
            *   **(Sub-Step 2.2: Attempt to Load `maia_project_state.json` - `Forge` leads for file reading, then hands content to `Catalyst`)**
                *   `(Forge)`: "I will now check for an existing project state file (`maia_project_state.json`) within `[Project_Directory_Path]`. Reading this file does not require explicit permission via Claude Code's prompt system as it's a read-only operation. Path to check: `[Project_Directory_Path]/maia_project_state.json`."
                *   `Forge` (as Claude) attempts to read the content of `[Project_Directory_Path]/maia_project_state.json`.
                *   **If `maia_project_state.json` is found and read successfully:**
                    *   `(Forge)`: "Project state file `maia_project_state.json` found and read. Content: \n\`\`\`json\n[Content_of_maia_project_state.json]\n\`\`\` \n I will now hand this over to `Catalyst` for processing. Do you approve switching back to the `Catalyst` persona? [Y/N]"
                    *   **User:** Responds [Y/N].
                    *   If User responds **Y**:
                        *   `(Catalyst)`: "Understood. I am `Catalyst`. I have the content of `maia_project_state.json`. I will now attempt to parse it and restore the session context."
                        *   **(Proceed to Sub-Step 2.3: `Catalyst` Processes State)**
                *   **If `maia_project_state.json` is NOT found (or read error occurs):**
                    *   `(Forge)`: "No existing project state file (`maia_project_state.json`) was found in `[Project_Directory_Path]` (or there was an error reading it: [brief error if available]). This will be treated as a new project session. I will now hand over to `Catalyst`. Do you approve switching back to the `Catalyst` persona? [Y/N]"
                    *   **User:** Responds [Y/N].
                    *   If User responds **Y**:
                        *   `(Catalyst)`: "Understood. I am `Catalyst`. No prior state file found or it was unreadable. We will proceed with a fresh project setup. The project directory `[Project_Directory_Path]` is ready."
                        *   `(Catalyst)`: "We have completed the User Session Initialization. What is the first MAIA-Workflow you would like to initiate for this project (e.g., 'Define Project Goals,' 'Develop New Feature')? Or would you like me to suggest some options?"
                        *   **(End of User Session Initialization Workflow for new projects)**
        *   If User responds **N** to initial `Forge` switch:
            *   `(Catalyst)`: "Understood. We cannot proceed with project directory setup without `Forge`'s system command capabilities. How would you like to proceed?"
*   **(Sub-Step 2.3: `Catalyst` Processes State from `maia_project_state.json`)**
    *   (This sub-step is only reached if `maia_project_state.json` was found, read, and its content passed to `Catalyst`.)
    *   **1. Parsing:** `Catalyst` attempts to parse the JSON content.
        *   **If parsing fails:**
            *   `(Catalyst)`: "I encountered an error parsing `maia_project_state.json`. The content appears to be invalid JSON. [Optional: show error snippet or first few lines of content]. Would you like to:
                A.  Ignore the state file and start a fresh session in `[Project_Directory_Path]`?
                B.  Attempt to view the raw content of the file (I will ask `Forge` to display it)? You could then try to fix it externally, and we can re-attempt loading.
                C.  Specify a path to a different backup state file if you have one?"
            *   User makes a decision. If A, proceed as "new project." If B or C, loop or re-attempt.
        *   **If parsing succeeds:** `Catalyst` now has a structured object representing the project state.
    *   **2. Validation & Context Restoration:** `Catalyst` validates expected fields in the parsed JSON (as per the defined `maia_project_state.json` structure: `schema_version`, `active_maia_workflow_instance`, etc.).
        *   `(Catalyst)`: "Validating schema version `[state.schema_version]` against my known version `[Catalyst_known_schema_version]`..."
        *   `Catalyst` attempts to restore its internal context based on these values (e.g., `active_maia_workflow_instance.workflow_name`, `.current_step_number`, `.workflow_variables`).
        *   **If critical information is missing, schema mismatch is unrecoverable, or state is inconsistent:**
            *   `(Catalyst)`: "The `maia_project_state.json` was parsed, but [e.g., 'is an incompatible schema version', 'is missing critical field X,' 'contains inconsistent data for Y']. How would you like to proceed? (Offer similar options to parsing failure, e.g., start fresh, attempt manual review/fix)."
        *   **If validation and context restoration are successful:**
            *   `(Catalyst)`: "Project state successfully loaded and validated from `maia_project_state.json`.
                We were working on MAIA-Workflow: **`[active_maia_workflow_instance.workflow_name]`**
                Instance ID: `[active_maia_workflow_instance.workflow_instance_id]`
                Resuming at Step **`[active_maia_workflow_instance.current_step_number]`**: '`[active_maia_workflow_instance.current_step_name]`'.
                Last status notes: '`[active_maia_workflow_instance.status_notes]`'.
                I am ready to resume from this point. Shall we proceed with Step `[active_maia_workflow_instance.current_step_number]`?"
            *   **(End of User Session Initialization Workflow for resumed projects)**
*   **User Actions (throughout Step 2):**
    *   Confirm persona switches [Y/N].
    *   Carefully review ICERC pre-briefs from `Forge` and then respond to Claude Code's native permission prompts [Y/N] for system commands.
    *   Provide decisions if `Catalyst` encounters issues loading or interpreting `maia_project_state.json`.
*   **Outputs (overall for Step 2):**
    *   `Project_Directory_Path` (internal context variable): The confirmed absolute path to the active project directory.
    *   The `claude` CLI's current working directory is effectively set to `Project_Directory_Path`.
    *   If `maia_project_state.json` existed and was valid:
        *   Restored session context (current MAIA-Workflow name, step, variables, etc.).
        *   `Catalyst` is ready to resume the loaded MAIA-Workflow.
    *   If `maia_project_state.json` did not exist or was invalid (and User chose to proceed as new):
        *   Session is initialized as a new project within the `Project_Directory_Path`.
        *   `Catalyst` is ready to start a new MAIA-Workflow.
*   **Completion Criteria (overall for Step 2 and this entire MAIA-Workflow):**
    *   Project directory is verified/created and the session's working context is aligned with it.
    *   Attempt to load/process `maia_project_state.json` is complete (either successfully resumed or determined to be a new project).
    *   `Catalyst` confirms readiness to proceed with project work (either resuming an existing MAIA-Workflow or starting a new one).

---
