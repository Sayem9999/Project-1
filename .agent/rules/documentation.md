---
description: Rules for documenting agent work and code.
globs: ["**/*"]
always_on: true
---

# Documentation Standards

## 1. Automated Commenting
- **Mandatory**: All new methods and classes must have docstrings.
- **Python**: Use PEP 8 style docstrings (Google or NumPy style).
- **TypeScript/JS**: Use JSDoc format.
- **Context**: Explain *why* a complex logic exists, not just *what* it does.

## 2. Artifact Generation
- **Primary Record**: Use Markdown artifacts for all significant work.
- **Types**:
    - `implementation_plan.md`: For planning complex changes.
    - `walkthrough.md`: For summarizing completed work and verification.
    - `architecture.md`: For system design changes.

## 3. Task Lists
- **Live Snapshot**: Maintain a `task.md` artifact.
- **Granulatiry**: Break down tasks into checkable steps.
- **Status**: Update status frequently (Pending -> In Progress -> Complete).

## 4. Commit Documentation
- **Format**: Use conventional commits (e.g., `feat:`, `fix:`, `chore:`).
- **Context**: Include the rationale in the commit body / PR description.
