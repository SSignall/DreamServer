# Open Interpreter

A natural language interface for computers that lets LLMs run code locally.

## Overview

Open Interpreter equips a function-calling language model with an `exec()` function, which accepts a language (like "Python" or "JavaScript") and code to run. It streams the model's messages, code, and your system's outputs to the terminal as Markdown.

## Features

- **Code Execution**: Run Python, JavaScript, Shell, and more locally
- **Chat Interface**: ChatGPT-like interface for natural language code generation
- **Browser Control**: Automate browser tasks for research
- **Data Analysis**: Plot, clean, and analyze large datasets

## Configuration

- **Port**: `OPENINTERPRETER_PORT` (default: 8000)
- **LLM API URL**: `LLM_API_URL` (default: `http://llama-server:8000`)
- **Data Directory**: `./data/open-interpreter`

## Usage

After installation, access the interface at `http://localhost:8000`

## Notes

- Open Interpreter will ask for user confirmation before executing code
- Run with `-y` flag to bypass confirmation (use with caution)
- Consider running in a restricted environment for safety
