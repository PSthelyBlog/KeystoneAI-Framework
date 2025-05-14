# Structure Definition: `maia_project_state.json`

**Version:** 1.0
**Date:** [Current Date - User to fill when saving]
**Designed By:** User & Catalyst

## 1. Purpose

The `maia_project_state.json` file is used by the AI-Assisted Framework (specifically by the `Catalyst` persona) to persist and restore the state of a project session. This allows users to resume work on a MAIA-Workflow across multiple interactive sessions with the `claude` CLI.

This file is typically located in the root of the `Project_Directory_Path`. It is generated or updated by `Catalyst` (directing `Forge` for the file write operation via ICERC) as part of the "Project State Consolidation & Export" step of any active project-specific MAIA-Workflow. It is read during the "User Session Initialization" MAIA-Workflow.

## 2. JSON Structure and Fields

```json
{
  "schema_version": "1.0.0",
  "last_updated_timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "framework_version_info": {
    "ai_assisted_dev_bible_version": "0.2.1",
    "maia_workflow_framework_version": "1.3.0",
    "catalyst_persona_version": "0.4.1", // Example
    "forge_persona_version": "0.1.1"    // Example
  },
  "project_info": {
    "project_name": "User-Defined Project Name (Optional)",
    "project_directory_path_at_save": "/path/to/project/on/previous/system"
  },
  "active_maia_workflow_instance": {
    "workflow_definition_source": "path/to/specific_maia_workflow_definition.md",
    "workflow_instance_id": "UUID-or-unique-identifier-for-this-run",
    "workflow_name": "Name of the MAIA-Workflow (e.g., 'Develop New Login Feature')",
    "current_step_number": 0,
    "current_step_name": "Human-readable name of the current step",
    "status_notes": "Brief human-readable status about the current state of the step.",
    "execution_mode_of_current_step": "Standard",
    "sub_maia_workflow_state_file_path": null,
    "workflow_variables": {
      "key_1": "value_1",
      "key_2": {
        "nested_key": "nested_value"
      }
    },
    "step_outputs_references": {
      "step_1_output_description": "relative/path/to/artifact_for_step1.md"
    }
  },
  "session_context": {
    "catalyst_notes_to_self": "User expressed interest in exploring X next.",
    "forge_last_known_environment_details": {
      "relevant_tool_versions": ["python@3.9.x", "node@18.x"],
      "key_project_dependencies_identified": ["library_foo_v1.2", "framework_bar_v2.3"]
    }
  },
  "pending_user_actions": [
    {
      "action_id": "PENDING_ICERC_XYZ",
      "description": "Awaiting User confirmation for an ICERC-presented command by Forge.",
      "details_reference": "logs/forge_icerc_pending_XYZ.log", // Optional path to more details
      "timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ],
  "artifact_manifest": [
    {
      "artifact_id": "RFI-FEATURE-001",
      "description": "Request for Implementation for Core Feature Alpha",
      "path_relative_to_project_dir": "rfis/RFI-FEATURE-001_v1.2.md",
      "version": "1.2",
      "last_modified_by_persona": "Catalyst",
      "last_modified_timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ",
      "tags": ["rfi", "feature-alpha", "pending-forge"]
    },
    {
      "artifact_id": "CODE-FEATURE-ALPHA-MAIN",
      "description": "Main source code file for Core Feature Alpha",
      "path_relative_to_project_dir": "src/feature_alpha/main.py",
      "version": "0.1-dev",
      "last_modified_by_persona": "Forge",
      "last_modified_timestamp_utc": "YYYY-MM-DDTHH:MM:SSZ",
      "tags": ["python", "source-code", "feature-alpha", "in-development"]
    }
  ]
}
```

## 3. Field Explanations

*   **`schema_version`** (String, Semantic Versioning e.g., "1.0.0"): Version of this `maia_project_state.json` schema. Essential for `Catalyst` to handle potential future changes to the state file structure.
*   **`last_updated_timestamp_utc`** (String, ISO 8601 Timestamp): The UTC timestamp indicating when this file was last saved.
*   **`framework_version_info`** (Object): Contains version information for the core framework components active when the state was saved. This helps in diagnosing compatibility issues if the framework documents are updated.
    *   `ai_assisted_dev_bible_version` (String): Version of the Dev Bible.
    *   `maia_workflow_framework_version` (String): Version of the MAIA-WF document.
    *   `catalyst_persona_version` (String, Optional): Version of the Catalyst persona definition.
    *   `forge_persona_version` (String, Optional): Version of the Forge persona definition.
*   **`project_info`** (Object): General information about the project.
    *   `project_name` (String, Optional): A human-readable name for the project, defined by the user.
    *   `project_directory_path_at_save` (String): The absolute path of the project directory when the state was last saved. This is for reference and might differ from the current session's project path if the project was moved.
*   **`active_maia_workflow_instance`** (Object, Can be `null` if no MAIA-Workflow is active): Details of the MAIA-Workflow that was in progress.
    *   `workflow_definition_source` (String): Path (relative to `Project_Directory_Path` or a known framework library path) to the `.md` file that defines the structure of this specific MAIA-Workflow type. `Catalyst` uses this to understand the steps.
    *   `workflow_instance_id` (String, UUID or similar): A unique identifier for this particular execution/instance of the MAIA-Workflow, distinguishing it if the same workflow type is run multiple times.
    *   `workflow_name` (String): Human-readable name of the MAIA-Workflow (e.g., "Develop New Login Feature").
    *   `current_step_number` (Integer, 0-indexed or 1-indexed as per convention): The step number within the `workflow_definition_source` that was about to start or was in progress.
    *   `current_step_name` (String): Human-readable name of the `current_step_number`.
    *   `status_notes` (String, Optional): Brief human-readable notes about the specific status of the current step (e.g., "Awaiting user feedback on design options," "Forge encountered an issue with dependency X").
    *   `execution_mode_of_current_step` (String: "Standard" | "Sub-MAIA-Workflow"): Indicates if the current step is a standard step or itself a nested MAIA-Workflow.
    *   `sub_maia_workflow_state_file_path` (String, Optional, Can be `null`): If `execution_mode_of_current_step` is "Sub-MAIA-Workflow", this points to the `maia_project_state.json` file specific to that sub-workflow.
    *   `workflow_variables` (Object): A key-value store for any dynamic data, parameters, or context variables relevant to the current state of this specific MAIA-Workflow instance. Values can be strings, numbers, booleans, arrays, or nested objects.
    *   `step_outputs_references` (Object, Optional): A key-value map where keys might be `step_[number]_output_[short_description]` and values are paths (relative to `Project_Directory_Path`) to key artifacts produced in completed steps of this workflow.
*   **`session_context`** (Object, Optional): Holds broader session information not strictly tied to a single MAIA-Workflow instance.
    *   `catalyst_notes_to_self` (String, Optional): Brief notes `Catalyst` might want to remember for overall project strategy or User preferences.
    *   `forge_last_known_environment_details` (Object, Optional): Information `Forge` might have gathered about the environment that could be useful context (e.g., checked tool versions, identified project dependencies). This should be treated as potentially stale and re-verified by `Forge` if critical.
*   **`pending_user_actions`** (Array of Objects, Optional): A list of actions that were pending from the User when the session was saved. This is a more experimental feature; its utility depends on how well `Catalyst`/`Forge` can re-establish the exact context for these pending actions.
    *   Each object can contain: `action_id` (String), `description` (String), `details_reference` (String, e.g., path to a log), `timestamp_utc` (String).
*   **`artifact_manifest`** (Array of Objects, Optional): An explicit, curated list of key project artifacts. This provides a structured inventory beyond just `step_outputs_references`. `Catalyst` or the User can use this to quickly get an overview of project deliverables.
    *   Each object can contain:
        *   `artifact_id` (String): A unique identifier for the artifact within the project.
        *   `description` (String): Human-readable description.
        *   `path_relative_to_project_dir` (String): Path to the artifact file.
        *   `version` (String, Optional): Version of the artifact.
        *   `last_modified_by_persona` (String: "Catalyst" | "Forge" | "User"): Who last significantly modified/generated it.
        *   `last_modified_timestamp_utc` (String): Timestamp of last modification.
        *   `tags` (Array of Strings, Optional): Keywords for categorization or search.

## 4. Handling by `Catalyst`

During the "User Session Initialization" MAIA-Workflow (Step 2, Sub-Step 2.3), `Catalyst` will:
1.  Attempt to parse this JSON file.
2.  Validate the `schema_version`. If incompatible, `Catalyst` will inform the User and discuss options (e.g., attempt migration if possible, start fresh).
3.  Restore its operational context based on `active_maia_workflow_instance` data, including loading the `workflow_definition_source` to understand the structure of the MAIA-Workflow being resumed.
4.  Re-populate `workflow_variables`.
5.  Use `session_context` for broader awareness.
6.  Optionally inform the User about `pending_user_actions`.
7.  Use the `artifact_manifest` for knowledge about existing project files.
8.  Inform the User about the resumed state and confirm readiness to proceed from the `current_step_number` of the `active_maia_workflow_instance`.

If no `maia_project_state.json` file is found, or if the User chooses to ignore an unrecoverable one, `Catalyst` will treat the session as a new project.
