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

## Getting Started

The KeystoneAI Framework provides multiple ways to get started, depending on your preferences and project structure.

### Method 1: Using the Utility Scripts (Recommended)

1. **Set up your API key:**
   ```bash
   export GEMINI_API_KEY=your_actual_gemini_api_key
   ```

2. **Run the framework directly:**
   ```bash
   cd KeystoneAI-Framework
   ./start_framework.sh
   ```
   This will initialize the framework with the default configuration.

3. **Run from another directory:**
   You can also install the framework scripts in any directory:
   ```bash
   cd KeystoneAI-Framework
   ./install_links.sh /path/to/your/project
   cd /path/to/your/project
   ./start_framework.sh
   ```

### Method 2: Using the Example Project

1. **Install scripts to the example project:**
   ```bash
   cd KeystoneAI-Framework
   ./install_links.sh ./example-project
   cd example-project
   ./start_framework.sh
   ```

2. **Or copy the example project:**
   ```bash
   # Example: Create a new project based on the example
   cp -r ~/KeystoneAI-Framework/example-project ~/my-projects/my-first-keystone-project
   cd ~/KeystoneAI-Framework
   ./install_links.sh ~/my-projects/my-first-keystone-project
   cd ~/my-projects/my-first-keystone-project
   ./start_framework.sh
   ```

### Method 3: Manual Setup

1. **Create configuration files in your project:**
   ```bash
   mkdir -p my-project/config
   cp ~/KeystoneAI-Framework/config/*.example my-project/config/
   # Remove .example extension
   cd my-project/config
   mv config.yaml.example config.yaml
   mv FRAMEWORK_CONTEXT.md.example FRAMEWORK_CONTEXT.md
   ```

2. **Run the framework with your config:**
   ```bash
   python ~/KeystoneAI-Framework/run_fixed.py
   ```

### Running for the First Time

When you start the framework, you should see:
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
    
    > I'd like to switch to Forge to discuss implementation.
    > /persona forge
    [System]: Active persona switched to Forge.
    
    > Can you implement a basic Python script for this project?
    (Forge): I'd be happy to implement a Python script for your project. Let me outline an approach based on the details you've provided...
    ```
*   **Utility Scripts:**
    * `restart_clean.sh`: Completely reset and restart the framework for a fresh state.
    * `clear_chat_history.sh`: Clear temporary files and chat history without restarting.
    * `diagnose_framework.py`: Check if your framework setup is correct and diagnose issues.

## Special Commands

Use these commands in the prompt for framework control:

*   `/help`: Shows available commands.
*   `/quit` or `/exit`: Exits the application.
*   `/clear`: Clears the conversation history (system prompts may be preserved).
*   `/system <message>`: Adds a new system-level instruction to the current conversation.
*   `/debug`: Toggles debug mode for more verbose output (useful for developers).
*   `/persona <id>`: Switches between AI personas (e.g., `/persona forge`, `/persona catalyst`).

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
*   **`QUICKSTART.md`**: Quick guide to get started with the framework.
*   **`PERSONA_SWITCHING.md`**: Guide to effectively switch between personas and troubleshoot issues.

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

This project is licensed under the MIT License. See the `LICENSE` file for details.
