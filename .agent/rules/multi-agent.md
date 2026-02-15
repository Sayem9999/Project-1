---
description: Rules for multi-agent collaboration and verification.
globs: ["**/*"]
always_on: true
---

# Multi-Agent Workflow Rules

## 1. Workspace Isolation
- **Constraint**: Treat the current workspace as the single source of truth for the active task.
- **Conflict Prevention**: Do not modify files outside the agreed-upon scope without conflict checks.

## 2. Role Assignment
- **Specialization**: Delegate tasks to the appropriate specialist agent:
    - **Frontend**: UI, React, CSS (`frontend_agent`).
    - **Backend**: API, Database, Python (`backend_agent`).
    - **Analyst**: Architecture, Schema (`analyst_agent`).
    - **Director/Creative**: Video vision (`director_agent`).

## 3. Verification Loops
- **Requirement**: "Verify with Artifacts" before marking a task complete.
- **Evidence**:
    - **Automated Tests**: Run `pytest` or `playwright`.
    - **Logs**: grep logs for success messages.
    - **Scripts**: Run ad-hoc verification scripts (e.g., `scripts/test_*.py`).
    - **Visuals**: Screenshots or browser recordings for UI changes.
- **Record**: Log evidence in `TEST_EVIDENCE.md`.

## 4. User-Triggered Workflows
- **Location**: Use `.agent/workflows/` for repeatable processes.
- **Optimization**: Trigger relevant workflows when a matching user intent is detected.
