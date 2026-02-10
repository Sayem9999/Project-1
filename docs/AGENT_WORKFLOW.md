# Agent Workflow Checklist (Project-Specific)

This checklist defines the integration workflow for ProEdit. Use it for all changes going forward.

## 1) Preparation & Planning
- Enable Planning Mode in the agent side panel before any code change.
- Enable Secure Mode so the agent asks for permission before sensitive commands or web requests.
- Load context with the @ command (or equivalent) for any impacted areas:
  - Frontend: `frontend/app`, `frontend/components`, `frontend/lib`
  - Backend: `backend/app`, `backend/alembic`, `backend/docs`
- Verify new changes against existing APIs and styles:
  - Backend: FastAPI routes, schemas, and error formats
  - Frontend: Next.js App Router patterns, UI components, and API client in `frontend/lib/api.ts`
- Produce:
  - Implementation Plan (what will change, why, and how)
  - Task List (concrete steps)

## 2) Automated Verification (Agentic Loop)
- Run the UI workflow with the Antigravity Browser Extension:
  - Login, upload, pipeline start, job detail, download
  - Admin console access if applicable
- Review artifacts:
  - Walkthrough (comment on deviations)
  - Code diff (scan for scope creep, API breaks)
  - Browser recordings (confirm workflow)

## 3) Safety & Stability Checks
- Confirm no secrets in code or logs.
- Confirm migrations if DB schema changed:
  - New Alembic file under `backend/alembic/versions`
  - Startup migrations complete in logs
- Validate API compatibility:
  - `GET /api/auth/me` returns expected fields
  - `POST /api/jobs/upload` still accepts existing payloads
- Run checks after changes:
  - Backend tests: `python -m pytest` (from repo root)
  - Frontend lint: `npm run lint` (from `frontend`)
  - Frontend build: `npm run build` (from `frontend`)
  - E2E: `npx playwright test` (from `frontend`)

## 4) Post-Change Synchronization
- Update docs if behavior changes:
  - `docs/DEPLOYMENT.md`
  - `README.md` (if user-facing)
- Record what changed and why (commit message + summary).
- Export and archive walkthrough artifacts if needed for team sharing.

## Quick Decision Matrix
- Backend-only change: update API docs + run backend tests.
- Frontend-only change: lint + build + E2E.
- Full-stack change: all checks + migration verification.

## Minimum Acceptance
- No failed tests or builds.
- No secrets committed.
- UI workflow tested end-to-end (recording checked).
