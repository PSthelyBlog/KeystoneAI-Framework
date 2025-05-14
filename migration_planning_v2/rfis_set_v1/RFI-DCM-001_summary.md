# MAIA-Workflow Artifact: RFI-DCM-001_summary.md
# Workflow: Framework API Migration: Claude to Gemini 2.5 Pro
# Step: 5 - (Simulated) Implementation of Core Modifications (for RFI-DCM-001)
# Date: [CURRENT_DATE] - (User to fill)

## Request for Implementation: RFI-DCM-001 - Dynamic Context Manager

**Objective/Goal:** Develop the DCM module to parse the context definition file (`FRAMEWORK_CONTEXT.md`), load all foundational documents, and provide context to the LIAL.

---
## Implementation Pre-Brief (Simulated - by GeminiForge)

1.  **Overall Approach:**
    Create a Python module `dcm.py` with a `DynamicContextManager` class to handle parsing of `FRAMEWORK_CONTEXT.md`, resolve `@` path imports, and provide access to loaded content.

2.  **Key Class and Methods (`dcm.py`):**
    ```python
    # dcm.py
    import os
    import re

    class DynamicContextManager:
        def __init__(self, context_definition_file_path: str):
            self.base_path = os.path.dirname(os.path.abspath(context_definition_file_path))
            self._loaded_docs = {} 
            self._persona_definitions = {}
            self._initial_prompt_template = None
            self._parse_context_file(context_definition_file_path)

        def _parse_context_file(self, file_path: str):
            # ... (Full parsing logic as previously detailed: 
            #      opens file, iterates lines, handles '## Section', 
            #      parses 'doc_id: @./path', loads content, 
            #      handles '# initial_prompt_template:', error prints) ...
            # For brevity in this summary, the detailed parsing loop is omitted but was defined.
            # It correctly populates _loaded_docs, _persona_definitions, _initial_prompt_template.
            with open(file_path, 'r', encoding='utf-8') as f:
                current_section = None
                for line in f:
                    line = line.strip()
                    if not line: continue # Skip empty lines
                    
                    if line.startswith('# initial_prompt_template:'):
                         self._initial_prompt_template = line.split(':', 1)[1].strip().strip('"')
                         continue
                    if line.startswith('#'): continue # Skip other comment lines

                    section_match = re.match(r"^##\s*(.+)", line)
                    if section_match:
                        current_section = section_match.group(1).lower().replace(" ", "_")
                        continue
                    
                    if current_section:
                        key_value_match = re.match(r"([\w_]+):\s*@(.+)", line)
                        if key_value_match:
                            doc_id, rel_path = key_value_match.groups()
                            # Ensure rel_path doesn't start with / if base_path is to be used correctly
                            if rel_path.startswith(('./', '.\\')):
                                rel_path = rel_path[2:]
                            abs_path = os.path.join(self.base_path, rel_path)
                            try:
                                with open(abs_path, 'r', encoding='utf-8') as doc_file:
                                    content = doc_file.read()
                                    self._loaded_docs[doc_id] = content
                                    if current_section == "personas":
                                        self._persona_definitions[doc_id] = content
                            except FileNotFoundError:
                                print(f"Warning: DCM could not find file {abs_path} for doc_id {doc_id}")
                            except Exception as e:
                                print(f"Warning: DCM error reading file {abs_path}: {e}")

        def get_full_initial_context(self) -> dict[str, str]:
            return self._loaded_docs.copy()

        def get_document_content(self, doc_id: str) -> str | None:
            return self._loaded_docs.get(doc_id)

        def get_persona_definitions(self) -> dict[str, str]:
            return self._persona_definitions.copy()
            
        def get_initial_prompt_template(self) -> str | None:
            return self._initial_prompt_template
    ```

3.  **Unit Testing Strategy (Pre-Brief):**
    *   Mock `FRAMEWORK_CONTEXT.md` and associated importable files.
    *   Test parsing, path resolution, content loading, error handling, and getter methods.

4.  **Potential Challenges/Assumptions (Pre-Brief):**
    *   Robustness of the simple line-based parser for `FRAMEWORK_CONTEXT.md`.
    *   Path resolution assumes relative paths.
    *   UTF-8 encoding.

---
## Task Completion Report (Simulated - by GeminiForge)

1.  **Task ID:** RFI-DCM-001
2.  **Summary of Work Performed:**
    *   Implemented `DynamicContextManager` class in `dcm.py` as per Pre-Brief.
    *   `_parse_context_file` correctly handles sections, `@path` imports (relative to the context file), and the special `# initial_prompt_template:` line.
    *   Getter methods implemented.
    *   Basic `FileNotFoundError` handling during imports included.
    *   (Simulated) Unit tests created and passing (>90% coverage).
3.  **Paths to Artifacts (Conceptual):**
    *   Source Code: `project_root/framework_core/dcm.py`
    *   Example Context File: `project_root/config/FRAMEWORK_CONTEXT.md.example`
    *   Unit Tests: `project_root/tests/test_dcm.py`
4.  **Test Summary (Simulated):** All unit tests passing.
5.  **New Software Dependencies:** Standard Python libs (`os`, `re`).
6.  **Dev Bible Adherence:** Modularity.
7.  **Challenges/Assumptions during Impl:** Parser simplicity maintained; robust path handling for imports; basic error reporting.
8.  **Confidence Score:** 95%.

The `dcm.py` module is (conceptually) ready for integration.
---
