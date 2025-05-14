# LLM Interaction Abstraction Layer (LIAL) Implementation

**Version:** 1.0.0
**Date:** [Current Date]
**Authors:** User & AI Team (Catalyst, Forge)

## 1. Overview

The LLM Interaction Abstraction Layer (LIAL) is a core component of the AI-Assisted Framework V2 architecture. It provides a standardized interface for interacting with different Large Language Models (LLMs), abstracting away the specific API details of each LLM provider. This allows the Framework Core to work with multiple LLMs through a consistent interface.

LIAL supports the ICERC protocol (Intent, Command, Expected Outcome, Risk Assessment, Confirmation Request) by ensuring that relevant text is preserved throughout the interaction flow.

## 2. Architecture

LIAL consists of two primary components:

1. **LIAL Core Interface**: Defines the abstract interface and data structures that all LLM adapters must implement.
2. **LLM-Specific Adapters**: Concrete implementations of the interface for specific LLM providers (currently Gemini).

```
+---------------------------+      +------------------------+
| Framework Core Application |<---->|          LIAL          |
| (run_framework.py)         |      | (LLM Interaction Abs.) |-----> (LLM API, e.g., Gemini)
+---------------------------+      |  - LLM Adapters        |
                                   |  - Msg Formatting      |
                                   +------------------------+
```

## 3. Key Components

### 3.1 LIAL Core Interface (`lial_core.py`)

The core interface defines:

- **Data Structures:**
  - `Message`: Represents a chat message with role, content, and optional tool-related fields
  - `ToolRequest`: Represents a request to execute a tool from the LLM
  - `LLMResponse`: Contains the conversational text from the LLM and an optional tool request
  - `ToolResult`: Represents the result of executing a tool

- **Abstract Interface:**
  - `LLMAdapterInterface`: Abstract base class that all LLM adapters must implement
  - Core methods: `__init__` and `send_message_sequence`

### 3.2 Gemini Adapter (`gemini_adapter.py`)

The Gemini adapter implements the `LLMAdapterInterface` for Google's Gemini API:

- Initializes the Google Generative AI SDK with the API key
- Defines tool schemas for Gemini including the `icerc_full_text` parameter
- Converts between our internal message format and Gemini's format
- Handles sending messages to Gemini and parsing responses
- Extracts function calls from responses and converts them to our ToolRequest format
- Supports persona management via the system instruction

## 4. Data Flow

### 4.1 Simple Conversation Flow

1. Framework Core receives user input
2. Framework Core sends a `Message` to LIAL's `send_message_sequence` method
3. LIAL converts the message to the LLM-specific format
4. LIAL calls the LLM API and receives a response
5. LIAL extracts the conversation text and returns an `LLMResponse`
6. Framework Core displays the conversation text to the user

### 4.2 Tool Execution Flow

1. Framework Core receives user input
2. Framework Core sends a `Message` to LIAL's `send_message_sequence` method
3. LIAL converts the message to the LLM-specific format
4. LIAL calls the LLM API and receives a response with a function call
5. LIAL extracts the function call details and converts them to a `ToolRequest`
6. LIAL returns an `LLMResponse` with the conversation text and `ToolRequest`
7. Framework Core sends the `ToolRequest` to TEPS for execution
8. TEPS displays the ICERC information and prompts the user for confirmation
9. TEPS executes the tool and returns a `ToolResult`
10. Framework Core sends the `ToolResult` back to LIAL
11. LIAL formats the tool result and sends it to the LLM
12. LIAL returns the LLM's response to Framework Core
13. Framework Core displays the response to the user

## 5. ICERC Protocol Support

LIAL supports the ICERC protocol by:

1. Declaring `icerc_full_text` as a required parameter in tool schemas
2. Including `icerc_full_text` in `ToolRequest` objects
3. Validating that `icerc_full_text` is present in function calls
4. Warning when `icerc_full_text` is missing and providing a fallback

## 6. Configuration

LIAL is configured via a configuration dictionary passed to the adapter's constructor:

```python
lial_config = {
    "api_key_env_var": "GEMINI_API_KEY",  # Environment variable for the API key
    "model_name": "gemini-1.5-pro-latest",  # Model to use
    "system_instruction_id": "system_instruction",  # ID for system instruction in DCM
    "generation_config": {  # Optional model configuration
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40
    }
}
```

## 7. Testing

LIAL includes both unit tests and integration tests:

- **Unit Tests:**
  - `test_lial_core.py`: Tests the core interface and data structures
  - `test_gemini_adapter.py`: Tests the Gemini adapter functionality
  
- **Integration Tests:**
  - `test_lial_integration.py`: Tests the interaction between LIAL, Framework Core, and TEPS

## 8. Usage Example

```python
from framework_core.lial_core import Message
from framework_core.adapters.gemini_adapter import GeminiAdapter

# Initialize the adapter
adapter = GeminiAdapter(
    config={
        "api_key_env_var": "GEMINI_API_KEY",
        "model_name": "gemini-1.5-pro-latest"
    },
    dcm_instance=dcm
)

# Send a message to the LLM
response = adapter.send_message_sequence(
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    active_persona_id="catalyst"
)

# Handle the response
print(response["conversation"])
if response["tool_request"]:
    # Handle tool request
    tool_result = teps.execute_tool(response["tool_request"])
    # Send tool result back to LLM
    next_response = adapter.send_message_sequence(
        messages=[
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": response["conversation"]},
            {
                "role": "tool_result",
                "content": json.dumps(tool_result["data"]),
                "tool_name": tool_result["tool_name"],
                "tool_call_id": tool_result["request_id"]
            }
        ],
        active_persona_id="catalyst"
    )
```

## 9. Future Enhancements

- **Additional LLM Adapters:** Implement adapters for other LLM providers (e.g., Claude, OpenAI)
- **Streaming Support:** Add support for streaming responses from LLMs
- **Rate Limiting & Retries:** Implement more robust handling of API rate limits
- **Improved Error Handling:** Add more granular error handling for different API errors
- **Performance Optimizations:** Add caching and connection pooling for efficiency