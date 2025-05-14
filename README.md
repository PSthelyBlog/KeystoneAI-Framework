# KeystoneAI-Framework (Version 2.0.0)

**The KeystoneAI-Framework is a powerful, LLM-agnostic system enabling structured AI collaboration for software development and complex projects. It's built on the LLM Agnostic Core Architecture (LACA), ensuring flexibility and robust operation.**

The framework features two primary AI personas:
*   **Catalyst**: The visionary strategist, architect, and AI team lead.
*   **Forge**: The expert AI implementer and system operator.

Guided by "The AI-Assisted Dev Bible" standards and utilizing the MAIA-Workflow framework, KeystoneAI helps orchestrate sophisticated tasks by leveraging the power of Large Language Models in a secure and controlled manner.

**Current Testing Status:** This version has been primarily tested with the **Google Gemini API**. The default Gemini model is set to **`gemini-2.5-flash-preview-04-17`** for its free-tier rate limits. More powerful models (e.g., `gemini-1.5-pro-latest`) are configurable but may encounter rate limits or require a billed Google Cloud account. Adapters for other LLM providers (e.g., Anthropic Claude, Azure OpenAI) are planned for future releases.

## Key Features (v2.0.0)

*   **LLM Agnostic Core Architecture (LACA)**:
    *   **LIAL (LLM Interaction Abstraction Layer)**: Communicate with various LLM providers (initially Gemini) through a consistent interface.
    *   **TEPS (Tool Execution & Permission Service)**: Securely execute system operations (file I/O, bash commands) with user confirmation via the ICERC protocol.
    *   **DCM (Dynamic Context Manager)**: Manage and load foundational documents (personas, standards, project context) to guide the LLM.
*   **Structured Collaboration**: Employs the MAIA-Workflow framework for breaking down complex tasks into manageable, AI-assisted steps.
*   **Persona-Driven Interaction**: Leverages distinct AI personas (Catalyst & Forge) for specialized roles in the development lifecycle.
*   **Enhanced Security**: Implements the ICERC (Intent, Command, Expected Outcome, Risk Assessment, Confirmation) protocol for all tool operations.
*   **Comprehensive Documentation**: Includes User Guide, Developer Guide, and API Reference.
*   **Configurable & Extensible**: Highly configurable and designed for developers to extend with new tools or LLM adapters.
*   **Example Project Included**: A ready-to-run `example-project` directory is provided to quickly get started.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.8+**
*   **Git**
*   **Google Gemini API Key**: Required for the default configuration.
*   *(API keys for other providers like Anthropic or Azure OpenAI will be needed if/when those adapters are used).*

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/PSthelyBlog/KeystoneAI-Framework.git
    cd KeystoneAI-Framework
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Linux/macOS:
    source venv/bin/activate
    # On Windows:
    # venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Keys (via Environment Variables):**
    The framework loads API keys from environment variables. For Gemini, set:
    ```bash
    export GEMINI_API_KEY=your_actual_gemini_api_key
    ```
    *(Note: Direct support for `.env` files is not included by default; environment variables are the primary method.)*

## Getting Started: Your First Use (Using the Example Project)

The easiest way to get started is by using the included `example-project`.

1.  **Copy the Example Project:**
    Navigate to a location where you want to create your project and copy the `example-project` folder from the cloned `KeystoneAI-Framework` repository.
    ```bash
    # Example: If KeystoneAI-Framework is in ~/KeystoneAI-Framework
    # and you want your project in ~/my-projects/
    mkdir -p ~/my-projects
    cp -r ~/KeystoneAI-Framework/example-project ~/my-projects/my-first-keystone-project
    cd ~/my-projects/my-first-keystone-project
    ```
    This `my-first-keystone-project` directory now contains a pre-configured `config` and `assets` structure.

2.  **Review Configuration (Optional, but Recommended):**
    Open `my-first-keystone-project/config/config.yaml`.
    *   The `llm.gemini.model` is likely pre-set to a generally accessible model like `gemini-2.5-flash-preview-04-17`. You can change this to `gemini-1.5-pro-latest` if you have access and an appropriate quota/billing setup.
    *   Verify that `dcm.context_definition_path` points correctly to `./config/FRAMEWORK_CONTEXT.md` (relative to where you'll run the script).

3.  **Run the Framework:**
    From within your new project directory (e.g., `my-first-keystone-project`):
    ```bash
    python /path/to/KeystoneAI-Framework/run_framework.py --config ./config/config.yaml
    ```
    *(Adjust `/path/to/KeystoneAI-Framework/` to the actual path where you cloned the framework.)*

    You should see initialization logs, then:
    ```
    [System]: Framework Core Application started. Type /help for available commands.
    ```
    Followed by Catalyst's initial message. If you encounter API errors (like 429 rate limit or model access issues for preview models), ensure your Gemini API key is active, billing is set up if required for the chosen model, or try a model with more lenient free tier access like `gemini-2.5-flash-preview-04-17`.

## Interacting with the Framework

*   Simply type your messages at the `>` prompt and press Enter.
*   The AI personas (Catalyst or Forge) will respond.
*   **Example Interaction:**
    ```
    > Hello Catalyst, I'd like to plan a new software project.
    (Catalyst): Excellent! I can help with that. Let's use the MAIA-Workflow to structure our planning. To begin, could you tell me a bit about the project's main goal?
    ```

## Special Commands

Use these commands in the prompt for framework control:

*   `/help`: Shows available commands.
*   `/quit` or `/exit`: Exits the application.
*   `/clear`: Clears the conversation history (system prompts may be preserved).
*   `/system <message>`: Adds a new system-level instruction to the current conversation.
*   `/debug`: Toggles debug mode for more verbose output (useful for developers).

## Working with Tools (TEPS & ICERC)

When an AI persona (usually Forge) needs to perform a system operation (like reading a file or running a command), the **TEPS** component will activate. It will present you with an **ICERC** brief:

*   **I**ntent: Why the tool is being used.
*   **C**ommand: What exact action will be performed.
*   **E**xpected **R**esult: What should happen if successful.
*   **C**onfirmation **R**equest: Asks for your explicit permission.

Type `Y` and press Enter to approve, or `N` to deny.

## Documentation

For more detailed information, please refer to:

*   **`docs/USER_GUIDE.md`**: Comprehensive guide for users (found in the main KeystoneAI-Framework repository).
*   **`docs/DEVELOPER_GUIDE_V2.md`**: For extending or contributing to the framework.
*   **`docs/api_reference.md`**: Detailed API documentation.

## Development & Testing

*   **Running Tests:** (From the root of the KeystoneAI-Framework repository)
    ```bash
    pytest tests/
    ```
    Or using `unittest` discovery:
    ```bash
    python -m unittest discover tests
    ```

## Contributing

Contributions are welcome! Please see `docs/DEVELOPER_GUIDE_V2.md` (in the main KeystoneAI-Framework repository) for guidelines.

## License

This project is licensed under the [Specify YOUR LICENSE HERE - e.g., MIT License]. See the `LICENSE` file for details.
