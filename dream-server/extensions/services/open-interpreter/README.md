# Open Interpreter Extension

Visual LLM code interpreter with auto-execution capabilities.

## Overview

Open Interpreter allows LLMs to run code on your computer securely. It provides a chat interface where the AI can write and execute Python code, bash commands, and more.

## Configuration

The extension uses the following environment variables:

- `LLM_API_URL`: URL to your LLM API endpoint (default: `http://localhost:8000/v1`)
- `OPENAI_API_KEY`: Dummy API key for compatibility (default: `dummy`)

## Ports

- External: `3005`
- Internal: `8000`

## Data Persistence

Code execution history and configurations are stored in:
```
./data/open-interpreter/
```

## Security

- Runs with `no-new-privileges:true` flag
- Resource limits: 2 CPUs, 4GB memory

## Healthcheck

The extension exposes a `/health` endpoint for monitoring.

## Usage

1. Start the extension: `dream enable open-interpreter`
2. Access the UI at `http://localhost:3005`
3. Start chatting with the AI code interpreter
