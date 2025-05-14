# Dynamic Context Manager (DCM) Implementation

**Version:** 1.0.0  
**Date:** 2025-05-13  
**Authors:** User & AI Team (Catalyst, Forge)  

## 1. Overview

The Dynamic Context Manager (DCM) is a core component of the AI-Assisted Framework V2 architecture. It is responsible for parsing the context definition file (`FRAMEWORK_CONTEXT.md`), loading referenced documents, and providing access to the loaded content. DCM enables the framework to maintain a well-organized collection of foundational documents like persona definitions, standards, and workflows that form the operational context for LLMs.

By centralizing context management, DCM ensures that all components of the framework have consistent access to critical documents and configuration. It supports the AI personas by providing them with their definitions and making other key resources available when needed.

## 2. Architecture

DCM is implemented as a standalone Python class (`DynamicContextManager`) within the `framework_core/dcm.py` module. It has minimal dependencies, relying only on standard Python libraries for file I/O and path manipulation.

DCM fits into the overall framework architecture as follows:

```
+---------------------------+      +--------------------------------+      +------------------------+
| User (Console Interface)  |<---->|   Framework Core Application   |<---->|          LIAL          |
+---------------------------+      | (run_framework.py)             |      | (LLM Interaction Abs.) |-----> (LLM API)
                                   |  - Main Interaction Loop       |      |  - LLM Adapters        |
                                   |  - Orchestrates LIAL,TEPS,DCM  |      |  - Msg Formatting      |
                                   +-----------+--------+-----------+      +------------------------+
                                               |        |
                                               |        | (ToolRequest)
                                   (Context)   |        | (ToolResult)
                                               V        V
                                   +-----------+--------+-----------+
                                   |          TEPS          |      |           DCM          |
                                   | (Tool Exec & Permission) |      | (Dynamic Context Mgr)  |
                                   |  - ICERC Display         |      |  - Parses FRAMEWORK_   |
                                   |  - User Y/N Prompt       |<---->|    CONTEXT.md          |
                                   |  - Executes Sys Ops      |      |  - Loads Docs          |
                                   +--------------------------+      +------------------------+
                                          |
                                          V (Sys Calls)
                                   +--------------------------+
                                   |   Local File System/OS   |
                                   +--------------------------+
```

### 2.1 Interactions with Other Components

- **Framework Core Application:** Initializes DCM and uses it to obtain initial context for LLMs
- **LIAL:** Uses DCM to access persona definitions and other context documents
- **TEPS:** May use DCM for configuration information
- **LLMs via LIAL:** Receive persona definitions, standards, and workflow documentation from DCM

## 3. Key Components

### 3.1 Context Definition File

The `FRAMEWORK_CONTEXT.md` file is a structured markdown document that defines which files should be loaded into the context and how they should be organized. The file follows a specific format:

- File starts with a title (`# Framework Context Definition`)
- Special directives like `# initial_prompt_template:` define configuration
- Sections defined by `## Section Name` group related documents
- Document references in the format `doc_id: @path/to/file.md` within sections

### 3.2 Document Types and Organization

DCM organizes documents into logical sections like:

- **Personas:** Definitions of AI personas like `Catalyst` and `Forge`
- **Standards:** Documentation of standards like the AI-Assisted Dev Bible
- **Workflows:** Workflow definitions like the MAIA-Workflow
- **Design Documents:** Project design documentation

These sections are used for organizational purposes and to identify special document types (e.g., personas).

### 3.3 DynamicContextManager Class

The core implementation is a Python class with the following key methods:

- **Initialization and Parsing:**
  - `__init__`: Initializes the DCM with a path to the context definition file
  - `_parse_context_file`: Parses the context definition file
  - `_load_document`: Loads a single document from a file path
  - `_resolve_path`: Resolves relative and absolute file paths

- **Public API:**
  - `get_full_initial_context`: Returns all loaded documents
  - `get_document_content`: Gets the content of a specific document
  - `get_persona_definitions`: Gets all persona definitions
  - `get_initial_prompt_template`: Gets the initial prompt template

## 4. Data Flow

### 4.1 Initialization Flow

1. Framework Core Application creates a DCM instance with a path to `FRAMEWORK_CONTEXT.md`
2. DCM parses the context file, identifying sections and document references
3. DCM loads each referenced document and stores it in its internal state
4. DCM identifies special documents (e.g., personas) and stores them separately
5. DCM extracts special directives like the initial prompt template

### 4.2 Context Access Flow

1. LIAL or other components request context from DCM (e.g., persona definition)
2. DCM retrieves the requested content from its internal state
3. Component uses the content as needed (e.g., LIAL includes persona in LLM prompt)

## 5. API Reference

### 5.1 Constructor

```python
def __init__(self, context_definition_file_path: str, encoding: str = "utf-8", logger: Optional[logging.Logger] = None):
    """
    Initialize the Dynamic Context Manager with a path to the context definition file.
    
    Args:
        context_definition_file_path: Path to the FRAMEWORK_CONTEXT.md file
        encoding: Character encoding for file operations (default: utf-8)
        logger: Optional logger instance for recording parsing progress and errors
    """
```

### 5.2 Public Methods

#### get_full_initial_context

```python
def get_full_initial_context(self) -> Dict[str, str]:
    """
    Return all loaded documents as a dictionary mapping doc_id to content.
    
    Returns:
        Dictionary mapping doc_id to document content
    """
```

#### get_document_content

```python
def get_document_content(self, doc_id: str) -> Optional[str]:
    """
    Get the content of a specific document by its ID.
    
    Args:
        doc_id: The identifier of the document
        
    Returns:
        Document content as string, or None if not found
    """
```

#### get_persona_definitions

```python
def get_persona_definitions(self) -> Dict[str, str]:
    """
    Get all persona definitions as a dictionary mapping persona_id to content.
    
    Returns:
        Dictionary mapping persona_id to persona definition content
    """
```

#### get_initial_prompt_template

```python
def get_initial_prompt_template(self) -> Optional[str]:
    """
    Get the initial prompt template if specified in the context file.
    
    Returns:
        Initial prompt template as string, or None if not specified
    """
```

## 6. Configuration Guide

### 6.1 Context Definition File Format

The `FRAMEWORK_CONTEXT.md` file follows this format:

```markdown
# Framework Context Definition v1.0

# initial_prompt_template: "Template text that the Framework Core can use to initialize the LLM"

## Personas
persona_id_1: @./path/to/persona1.md
persona_id_2: @./path/to/persona2.md

## Standards
standard_id: @./path/to/standard.md

## OtherSection
document_id: @./path/to/document.md
```

#### Special Syntax

- **Section Headers:** `## SectionName` creates a new section
- **Document References:** `doc_id: @path/to/file.md` references a document
  - Paths can be:
    - Relative to the context file location (`@./file.md` or `@../file.md`)
    - Absolute (`@/absolute/path/to/file.md`)
- **Special Directives:** `# directive_name: value` sets configuration
  - Currently supported: `# initial_prompt_template: "template text"`

### 6.2 Setting Up a New Context Definition

1. Create a directory for your project configuration (e.g., `config/`)
2. Create `FRAMEWORK_CONTEXT.md` in this directory
3. Define sections and document references based on your project structure
4. Add any special directives like `initial_prompt_template`
5. Reference the context file when initializing the DCM

### 6.3 Document ID Conventions

Document IDs should follow these conventions:
- Use lowercase with underscores
- Use a prefix indicating the document type (e.g., `persona_`, `standard_`, `workflow_`)
- Keep IDs short but descriptive
- Examples: `persona_catalyst`, `standard_dev_bible`, `workflow_maia`

## 7. Usage Examples

### 7.1 Basic Initialization and Access

```python
from framework_core.dcm import DynamicContextManager

# Initialize DCM with a path to the context definition file
dcm = DynamicContextManager("/path/to/config/FRAMEWORK_CONTEXT.md")

# Get a specific document
dev_bible = dcm.get_document_content("standard_dev_bible")
if dev_bible:
    print(f"Loaded Dev Bible, length: {len(dev_bible)} characters")

# Get all persona definitions
personas = dcm.get_persona_definitions()
print(f"Loaded {len(personas)} personas: {', '.join(personas.keys())}")

# Get the initial prompt template
template = dcm.get_initial_prompt_template()
if template:
    print(f"Initial prompt template: {template[:50]}...")
```

### 7.2 Integration with LIAL

```python
from framework_core.dcm import DynamicContextManager
from framework_core.adapters.gemini_adapter import GeminiAdapter

# Initialize DCM
dcm = DynamicContextManager("/path/to/config/FRAMEWORK_CONTEXT.md")

# Initialize Gemini adapter with DCM
adapter = GeminiAdapter(
    config={
        "api_key_env_var": "GEMINI_API_KEY",
        "model_name": "gemini-1.5-pro-latest"
    },
    dcm_instance=dcm
)

# Send a message to the LLM using a persona from DCM
response = adapter.send_message_sequence(
    messages=[{"role": "user", "content": "Hello, how can you help me?"}],
    active_persona_id="persona_catalyst"  # This references a persona loaded by DCM
)
```

### 7.3 Using with Framework Core (Future Implementation)

```python
from framework_core.dcm import DynamicContextManager

# Initialize DCM
dcm = DynamicContextManager("./config/FRAMEWORK_CONTEXT.md")

# Get the initial prompt template
initial_prompt = dcm.get_initial_prompt_template()

# Initialize other components with DCM
lial = initialize_lial(config, dcm)
teps = initialize_teps(config)

# Start the main interaction loop with the initial prompt
start_interaction_loop(lial, teps, initial_prompt)
```

## 8. Error Handling and Troubleshooting

### 8.1 Common Errors

#### File Not Found

If a context file or referenced document can't be found:
- Verify the path is correct
- Check if the file exists in the specified location
- If using relative paths, ensure they're relative to the context file location

```
ERROR - dcm - Context file not found: /path/to/FRAMEWORK_CONTEXT.md
```

```
WARNING - dcm - Document file not found: /path/to/document.md
```

#### Parsing Errors

If the context file format is incorrect:
- Check the syntax of document references (`doc_id: @path/to/file.md`)
- Ensure section headers start with `##` followed by a space
- Verify special directives start with `#` followed by a space

```
ERROR - dcm - Error parsing context file: invalid syntax on line N
```

#### Security Warnings

If a path traversal attempt is detected:
- Check for suspicious patterns in file paths (e.g., `../../../etc/passwd`)
- Review document references for security issues

```
WARNING - dcm - Suspicious path detected, may be a directory traversal attempt: ../../../etc/passwd
```

### 8.2 Debugging Tips

1. **Enable Verbose Logging:**
   - Create a custom logger with DEBUG level
   - Pass it to the DCM constructor

   ```python
   import logging
   logger = logging.getLogger("dcm_debug")
   logger.setLevel(logging.DEBUG)
   handler = logging.StreamHandler()
   handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
   logger.addHandler(handler)
   
   dcm = DynamicContextManager(context_path, logger=logger)
   ```

2. **Check Loaded Documents:**
   - Use `get_full_initial_context()` to see all loaded documents
   - Verify the document IDs match your expectations

3. **Examine Log Messages:**
   - Look for warnings and errors in the logs
   - Check for unexpected line parsing issues

## 9. Integration with Other Components

### 9.1 Integration with LIAL

The DCM component is designed to work closely with the LIAL component. LIAL adapters take a DCM instance in their constructor and can access persona definitions and other context documents using the DCM's methods.

Key integration points:
- LIAL adapters use `dcm.get_document_content()` to access persona definitions and other documents
- LIAL adapters may use `dcm.get_persona_definitions()` to get all personas
- LIAL may use `dcm.get_initial_prompt_template()` to retrieve the initial prompt

### 9.2 Integration with Framework Core (Future)

The Framework Core will initialize the DCM with a path to the context definition file and pass the DCM instance to other components that need it.

Planned integration:
- Framework Core initializes DCM early in the startup process
- Framework Core uses the initial prompt template from DCM
- Framework Core passes DCM to LIAL when initializing

## 10. Testing

DCM includes comprehensive unit and integration tests:

- **Unit Tests**: `/tests/unit/framework_core/test_dcm.py`
  - Tests the core functionality of the DCM class
  - Tests parsing, path resolution, document loading, and context access

- **Integration Tests**: `/tests/integration/test_dcm_lial_integration.py`
  - Tests the integration between DCM and LIAL
  - Tests that LIAL can access documents from DCM

Run tests using pytest:

```bash
pytest tests/unit/framework_core/test_dcm.py -v
pytest tests/integration/test_dcm_lial_integration.py -v
```

## 11. Future Enhancements

Potential future enhancements for the DCM component include:

1. **Context Validation**: Validate that required documents exist and have the expected format
2. **Dynamic Reload**: Ability to reload the context when files change
3. **Caching**: Optimize document loading with caching
4. **Extended Directives**: Support for additional special directives beyond `initial_prompt_template`
5. **Section-specific Processing**: Special handling for different document types
6. **Environment Variable Expansion**: Support for environment variables in file paths
7. **Improved Security**: Enhanced path validation and restriction

## 12. Conclusion

The Dynamic Context Manager is a foundational component of the AI-Assisted Framework V2 that enables consistent access to personas, standards, workflows, and other important documents. By centralizing context management, it ensures that all components of the framework have access to the same information and configuration.

DCM's simple API and flexible configuration make it easy to adapt to different project structures and requirements, while its robust error handling and logging make it reliable and debuggable. As the framework evolves, DCM will continue to play a critical role in managing the shared context that all components rely on.