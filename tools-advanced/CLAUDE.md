# CLAUDE.md

## Project Overview
This project, named `tools-advanced`, explores and demonstrates advanced concepts in agent development, particularly focusing on various tool-use behaviors and agent execution flows. It showcases how to integrate and manage tools within an agentic system.

## Technology Stack
*   **Python**: The primary programming language used.
*   **openai-agents**: A library for building and orchestrating agents.
*   **python-dotenv**: For loading environment variables from a `.env` file.
*   **AsyncOpenAI**: An asynchronous client for interacting with OpenAI-compatible APIs (used here with Gemini).
*   **Gemini Model**: Specifically `gemini-2.5-flash` is used for agent interactions.
*   **uv**: A fast Python package installer and resolver, indicated by `uv.lock` and `pyproject.toml`.

## Directory Structure
```
.
├── .env
├── .python-version
├── .venv/
├── 01_stop_on_first_tool.py
├── 02_StopAtTools.py
├── 03_max_turns_in_runner.py
├── 04_exceptions_in_tool.py
├── README.md
├── main.py
├── pyproject.toml
└── uv.lock
```

## Coding Conventions
*   **Environment Variables**: Sensitive information and API keys are loaded from a `.env` file.
*   **Agent Tracing**: The `set_tracing_disabled(False)` call suggests that agent execution tracing is enabled or a key feature for development and debugging.
*   **Tool Definitions**: Tools for agents are defined using the `@function_tool` decorator, including docstrings for clarity.
*   **Imports**: Standard Python import conventions are followed, with imports placed at the top of the file.
*   **Asynchronous Operations**: Uses `AsyncOpenAI` for potentially asynchronous interactions with models.

## Key Commands
*   **Install Dependencies**: Given `pyproject.toml` and `uv.lock`, you would typically use `uv` to manage dependencies.
    ```bash
    uv pip install
    ```
*   **Run a specific agent example**:
    ```bash
    python 01_stop_on_first_tool.py
    ```
    (Replace `01_stop_on_first_tool.py` with the desired script to run other examples.)

## Important Notes
*   Ensure a `.env` file is present in the root directory with `GEMINI_API_KEY` and `BASE_URL` defined for the agents to function correctly.
*   The project utilizes the `stop_on_first_tool` behavior for agent tool use, meaning the agent will stop generation and execute the first tool call it decides to make.
*   This project appears to be a collection of examples demonstrating different aspects of agent interaction and tool handling.
