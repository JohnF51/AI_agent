# Local AI Agent with Google Antigravity SDK and 'uv'

This project demonstrates how to build and run your own autonomous AI agent using the `google-antigravity` library and the `uv` package manager.

## Quick Start (Automatic Installation)

To automatically install `uv`, Python, and all required dependencies, simply run the **`setup.bat`** script (e.g., by double-clicking it or running it in your terminal):

```cmd
setup.bat
```

The script will automatically:
1. Check for/install the `uv` package manager.
2. Install Python version 3.12.
3. Create a local virtual environment `.venv`.
4. Install `google-antigravity` and other requirements from `requirements.txt`.

After installation is complete, run the agent using:
```bash
uv run main.py
```

---

## Manual Installation

If you prefer a manual, step-by-step installation, follow these instructions:

### 1. Install `uv`
- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- Or via **pip**:
  ```bash
  pip install uv
  ```

### 2. Install Python
```bash
uv python install 3.12
```

### 3. Create and Activate the Virtual Environment
```bash
uv venv --python 3.12
```

Activation:
- **PowerShell:** `.venv\Scripts\Activate.ps1`
- **CMD:** `.venv\Scripts\activate.bat`

### 4. Install Dependencies
```bash
uv pip install -r requirements.txt
```

### 5. Run the Agent
```bash
uv run main.py
```

---

## Git Auto-Watcher (Auto-Commit & Auto-Push)

If you are working with an AI assistant in this repository, you can enable automatic tracking of code changes. The assistant will write files locally, and the watcher will automatically commit and push them to your Git repository in real-time.

To start the watcher, run:
```bash
python git_watcher.py
```

---

## Try These Prompts in Chat
1. **Get System Information:** Ask the agent: *"What is the system information?"* or *"Check free disk space on C:"*.
2. **Security Test (Human-in-the-Loop):** Order the agent: *"Run whoami command"* or *"Show files in folder"*. The agent will request your explicit approval before executing any shell command.
