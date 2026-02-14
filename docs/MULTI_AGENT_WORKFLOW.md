# Multi-Agent Workflow

Yes, you can use multiple specialized agents/roles.

This document defines role boundaries and handoffs for:
- Frontend Developer
- Backend Developer
- Analyst
- UI Tester
- Release Coordinator (optional)

## Role Responsibilities

## Frontend Developer
- Owns `frontend/` UI, UX behavior, API integration, and client errors.
- Must document:
  - UI behavior changed
  - Why the UX/API change was needed
  - Screenshots/test results in `TEST_EVIDENCE.md`

## Backend Developer
- Owns `backend/` APIs, services, DB behavior, orchestration, performance.
- Must document:
  - Endpoint/service/model changes
  - Why the contract or logic changed
  - Migration/risk notes

## Analyst
- Owns problem framing, root-cause analysis, metrics, and incident summaries.
- Must document:
  - Bug root cause in `BUG_REGISTER.md`
  - Decision tradeoffs in `DECISION_LOG.md`
  - Impact/risk assessment

## UI Tester
- Owns validation of user flows and regressions.
- Must document:
  - Test scope and procedures
  - Pass/fail outcomes
  - Repro steps for failures

## Release Coordinator (Optional)
- Owns release readiness checks and final signoff.
- Ensures all related logs are complete before deploy.

## Required Handoff Sequence
1. Analyst opens/updates `WORK_ITEMS.md` and (if bug) `BUG_REGISTER.md`.
2. Backend/Frontend roles implement changes.
3. Each implementation adds an entry to `CHANGE_LOG.md`.
4. UI Tester logs validation in `TEST_EVIDENCE.md`.
5. If tradeoff/architecture changed, add `DECISION_LOG.md`.
6. Mark work item done only after docs are complete.

## Minimum Documentation Checklist Per Change
- `CHANGE_LOG.md` updated
- `BUG_REGISTER.md` updated (if bug)
- `TEST_EVIDENCE.md` updated
- `DECISION_LOG.md` updated (if non-trivial decision)

