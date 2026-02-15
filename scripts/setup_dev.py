import os
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()
VSCODE_DIR = ROOT_DIR / ".vscode"
LOGS_DIR = ROOT_DIR / "logs"

def create_vscode_settings():
    VSCODE_DIR.mkdir(exist_ok=True)
    
    settings = {
        "files.exclude": {
            "**/.git": True,
            "**/.svn": True,
            "**/.hg": True,
            "**/CVS": True,
            "**/.DS_Store": True,
            "**/Thumbs.db": True,
            "**/__pycache__": True,
            "**/.venv": True,
            "**/.pytest_cache": True,
            "**/.mypy_cache": True,
            "**/.ruff_cache": True
        },
        "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/Scripts/python.exe",
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.autoImportCompletions": True,
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.fixAll": "explicit",
                "source.organizeImports": "explicit"
            }
        },
        "[typescript]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "editor.formatOnSave": True
        },
        "[typescriptreact]": {
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "editor.formatOnSave": True
        },
        "eslint.workingDirectories": ["./frontend"]
    }
    
    with open(VSCODE_DIR / "settings.json", "w") as f:
        json.dump(settings, f, indent=2)
    print(f"Created {VSCODE_DIR / 'settings.json'}")

def create_extensions():
    VSCODE_DIR.mkdir(exist_ok=True)
    extensions = {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "charliermarsh.ruff",
            "dbaeumer.vscode-eslint",
            "esbenp.prettier-vscode",
            "tamasfe.even-better-toml"
        ]
    }
    with open(VSCODE_DIR / "extensions.json", "w") as f:
        json.dump(extensions, f, indent=2)
    print(f"Created {VSCODE_DIR / 'extensions.json'}")

def create_launch_config():
    VSCODE_DIR.mkdir(exist_ok=True)
    launch = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Backend: API",
                "type": "python",
                "request": "launch",
                "module": "uvicorn",
                "args": ["app.main:app", "--reload", "--port", "8000"],
                "cwd": "${workspaceFolder}/backend",
                "env": {"ENVIRONMENT": "development"},
                "justMyCode": True
            },
            {
                "name": "Backend: Celery Worker",
                "type": "python",
                "request": "launch",
                "module": "celery",
                "args": ["-A", "app.celery_app", "worker", "--loglevel=info", "--pool=solo"],
                "cwd": "${workspaceFolder}/backend",
                "env": {"ENVIRONMENT": "development"}
            },
            {
                "name": "Frontend: Dev",
                "type": "node",
                "request": "launch",
                "runtimeExecutable": "npm",
                "runtimeArgs": ["run", "dev"],
                "cwd": "${workspaceFolder}/frontend",
                "console": "integratedTerminal"
            }
        ]
    }
    with open(VSCODE_DIR / "launch.json", "w") as f:
        json.dump(launch, f, indent=2)
    print(f"Created {VSCODE_DIR / 'launch.json'}")

def create_editorconfig():
    content = """root = true

[*]
charset = utf-8
indent_style = space
indent_size = 4
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{js,jsx,ts,tsx,json,css,scss,html,yml,yaml}]
indent_size = 2

[*.py]
indent_size = 4
"""
    with open(ROOT_DIR / ".editorconfig", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {ROOT_DIR / '.editorconfig'}")

def ensure_logs():
    LOGS_DIR.mkdir(exist_ok=True)
    (LOGS_DIR / ".keep").touch()
    print(f"Ensured {LOGS_DIR} exists")

def main():
    print("Setting up development environment...")
    create_vscode_settings()
    create_extensions()
    create_launch_config()
    create_editorconfig()
    ensure_logs()
    print("Environment setup complete.")

if __name__ == "__main__":
    main()
