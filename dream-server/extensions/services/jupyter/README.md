# Jupyter Extension for Dream Server

## Overview

Jupyter Notebook is an open-source web application for creating and sharing computational documents. This extension provides a full-featured data science environment with Python, scipy stack, and GPU support.

## Features

- JupyterLab interface (modern, extensible)
- Pre-installed: NumPy, Pandas, SciPy, Matplotlib, Scikit-learn
- GPU acceleration support (CUDA-enabled)
- Persistent storage for notebooks
- Optional token-based authentication

## Usage

### Enable the extension

```bash
dream extensions enable jupyter
```

### Access Jupyter

```
http://localhost:${JUPYTER_PORT:-8888}
```

If `JUPYTER_TOKEN` is set, use it to log in. If empty (default), no authentication required.

### Set a custom token

Edit `.env`:

```
JUPYTER_TOKEN=your-secret-token
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `JUPYTER_PORT` | 8888 | Web UI port |
| `JUPYTER_TOKEN` | (empty) | Auth token (empty = no auth) |

## Integration

Jupyter connects to Dream Server's LLM API:
- Use `${LLM_API_URL}` in notebooks for API calls
- Query local models directly from Python code

Example:
```python
import requests

response = requests.post(f"{os.environ['LLM_API_URL']}/v1/chat/completions", ...)
```

## Uninstall

```bash
dream extensions disable jupyter
```

Notebooks in `./data/jupyter/` are preserved.
