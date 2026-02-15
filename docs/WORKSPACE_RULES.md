# Workspace Rules & Guidelines

This document serves as the **Single Source of Truth** for all development standards, agent behaviors, and verification protocols in this workspace.

> **CRITICAL**: All AI Agents and Developers must adhere to these rules.

## 1. Multi-Agent Workflow

### Role Assignment
- **Frontend Agent**: Use for React, Next.js, Tailwind, UI/UX (`/api/maintenance/frontend`).
- **Backend Agent**: Use for FastAPI, Python, Celery, Database (`/api/maintenance/backend`).
- **Analyst Agent**: Use for Architecture, Schema Design, Requirements (`/api/maintenance/analyst`).
- **Director Agent**: Use for creative vision and video flow (`director_agent`).

### Workspace Isolation
- **Constraint**: Treat the current workspace as the only truth.
- **Conflict Prevention**: Do not modify files outside the agreed scope.

## 2. Development Standards

### Backend
- **Schema First**: Update `schemas.py` and `models.py` together for any data change.
- **JSON Robustness**: Use `parse_json_response` (from `backend/app/agents/base.py`) for all LLM outputs.
- **Dependency Audit**: Check `requirements.txt` before adding new libs. Prefer existing tools (FFmpeg, etc.).

### Frontend
- **Component Consistency**: Use Vanilla CSS and Lucide-React. No new utility libraries.
- **Glassmorphism**: Use `glass-panel` and `shadow-glow` classes.
- **Data Bento**: Add specialist insights as modular cards in the Job Status grid.

## 3. Documentation & Verification

### Rules for Agents
1.  **Verify First**: No task is complete without Evidence (Logs, Script Output, Tests).
2.  **Artifacts**: Maintain `task.md` and `walkthrough.md` as live records.
3.  **Process**:
    *   **Plan**: Create `implementation_plan.md` for complex changes.
    *   **Execute**: Write code with JSDoc/PEP8 comments.
    *   **Verify**: Run tests/scripts and log results in `TEST_EVIDENCE.md`.
    *   **Document**: Update `CHANGE_LOG.md` with conventional commit style.

### Tracking IDs
Use strict ID formats in documentation:
- `WRK-YYYYMMDD-NNN` (Work Items)
- `BUG-YYYYMMDD-NNN` (Bugs)
- `CHG-YYYYMMDD-NNN` (Changes)
- `TST-YYYYMMDD-NNN` (Tests)

## 4. Environment Persistence
- **Production Path**: `C:\pinokio\api\editstudio` (Active Pinokio Project).
- **Staging/Dev Path**: `C:\Users\Sayem\Downloads\New folder\Project-1-1` (Git Repo).
- **Rule**: Always verify which environment you are modifying. configuration changes must be mirrored to the Production Path.
- **Setup**: Run `make setup-ide` (in `backend/`) to restore `.vscode`, `.editorconfig`, and `logs/`.
- **Reference**: See `docs/DEVELOPMENT_SETUP.md`.

## 5. Technical Co-Founder Protocols

### Phase 1: Pre-Change Impact Analysis
Before any significant change, map "ripple effects":
1.  **Dependency Mapping**: Identify upstream/downstream systems.
2.  **Functional Review**: Check for conflicts with existing requirements.
3.  **Resource Assessment**: Quantify impact on memory/network.
4.  **Backward Compatibility**: Confirm no breaking changes for fielded systems.

### Phase 2: Integration Verification
1.  **Small Commits**: Incremental batches.
2.  **Feature Flags**: Toggle new features safely.
3.  **Automated Builds**: CI triggers on every commit.

### Phase 3: Comprehensive Testing (Pyramid)
1.  **Unit**: Individual components.
2.  **Integration**: Module communication.
3.  **Regression**: Re-run old tests.
4.  **Smoke**: Health checks post-deployment.
5.  **Environment Parity**: Staging mirrors production.

### Phase 4: Deployment & Maintenance
1.  **Single Artifact**: Same build for all envs.
2.  **Automated Rollback**: Revert if error rate > 5%.
3.  **Docs-as-Code**: Update manuals with code.
4.  **Monitoring**: Track latency/errors/conversion.

## 6. The 7-Agent Audit Protocol (Hardcoded)
**Mission**: Execute Parallel Full-Stack Audit targeting Backend + Frontend (Web/Mobile).

### Sub-Agents & Roles
1.  **The Logic Squad (Alpha)**: Backend logic, edge cases, race conditions.
2.  **The Security Detail (Bravo)**: OWASP Top 10, secrets, sanitization.
3.  **The UX/Performance Team (Charlie/Delta)**:
    *   **Charlie (Web)**: React/Next.js best practices, re-renders.
    *   **Delta (Mobile)**: Flutter performance, main-thread blocking.
4.  **The Integration Hawks (Echo/Foxtrot)**:
    *   **Echo (Web-Bridge)**: Verify Frontend API calls vs Backend schema.
    *   **Foxtrot (Mobile-Bridge)**: Verify Mobile API calls vs Backend schema.
5.  **The Synthesizer (Omega)**: Group findings by SEVERITY, deduplicate, and report.
