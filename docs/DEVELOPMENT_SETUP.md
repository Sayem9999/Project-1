# Development Environment Setup

To ensure your development environment (VSCode settings, logs, formatting rules) persists across sessions and fresh clones, we have automated the setup process.

## Quick Start
Run the following command from the `backend/` directory:

```bash
make setup-ide
# OR as part of full setup:
make dev-setup
```

## What This Does
The `scripts/setup_dev.py` script automatically:
1.  **VSCode Configuration**: Creates `.vscode/settings.json`, `extensions.json`, and `launch.json` for Python/TypeScript debugging and linting.
2.  **EditorConfig**: Creates `.editorconfig` for consistent coding styles.
3.  **Logs**: Ensures the `logs/` directory exists with a `.keep` file (so it persists in Git).

## Troubleshooting "Forgotten" Settings
If Antigravity or VSCode seems to "forget" your settings:
1.  Run `make setup-ide` to regenerate the configuration files.
2.  Ensure you are opening the repository root (`Project-1-1`) in VSCode, not a subdirectory.
