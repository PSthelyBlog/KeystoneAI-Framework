# Persona Switching Guide for KeystoneAI Framework

This guide explains how to effectively switch between personas in the KeystoneAI Framework.

## Understanding Personas

The framework includes two main personas:

1. **Catalyst** - The Visionary AI Strategist & Architect
   - Focuses on high-level strategy, architecture, and planning
   - Helps with project organization and conceptual design
   - Default persona when starting the framework

2. **Forge** - The Expert AI Implementer & System Operator
   - Focuses on technical implementation and system operations
   - Provides detailed code and practical solutions
   - Uses the ICERC protocol for system safety

## Basic Persona Switching

To switch between personas:

```
/persona forge     # Switch to Forge persona
/persona catalyst  # Switch to Catalyst persona
```

## Troubleshooting Persona Issues

### Incorrect Persona Identification

If the AI responds with the wrong persona (e.g., identifies as "Catalyst" when you switched to "Forge"):

1. **Try a clean restart**:
   ```bash
   ./restart_clean.sh
   ```

2. **Reset conversation history**:
   ```
   /clear
   ```
   Then type your message to see if the persona responds correctly.

3. **Use explicit prompting**:
   After switching personas, remind the AI which persona it should be:
   ```
   Remember that you are now Forge, not Catalyst. Please provide your response as Forge.
   ```

### Command Not Working

If the `/persona` command fails with "Invalid persona ID":

1. **Verify configuration**:
   ```bash
   python diagnose_framework.py
   ```
   This will check if the personas are properly loaded.

2. **Restart with clean state**:
   ```bash
   ./restart_clean.sh
   ```

3. **Check for section headers**:
   Make sure your `FRAMEWORK_CONTEXT.md` has the correct section for personas:
   ```
   ## Core Persona Definitions
   ```

## Advanced Persona Topics

### When to Use Each Persona

- **Use Catalyst** for:
  - Project planning and organization
  - Architecture decisions
  - High-level strategy
  - Requirements gathering

- **Use Forge** for:
  - Implementation tasks
  - Coding and debugging
  - System operations
  - Tool usage with ICERC protocol

### Customizing Personas

If you need to modify the persona behaviors:

1. Edit the persona definition files:
   - `assets/personas/catalyst_persona.md`
   - `assets/personas/forge_persona.md`

2. Update the system prompts in `FRAMEWORK_CONTEXT.md`

3. Restart the framework to apply changes:
   ```bash
   ./restart_clean.sh
   ```