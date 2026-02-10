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

---

# CODEX OPERATIONAL MANUAL — ONE PAGE

## 1) Define Clear Intent
- State goal, success criteria, and constraints.
- Write prompts like concrete GitHub issues (file paths, goals, tests) ([OpenAI][1]).
- Example:
  - “In `src/api/user.py`, add pagination to `get_users()`. Write tests for pagination edge cases.”

## 2) Structure Work as Tasks
- Break changes into small, focused tasks:
  - Add tests first
  - Implement feature
  - Refactor with tests
  - Review results
- Codex performs best with incremental tasks under ~1 hour ([OpenAI][1]).

## 3) Use Ask Mode First
- For big tasks:
  - Ask for a plan
  - Review the plan
  - Use the plan to generate code
- This two-phase workflow reduces errors and rewrites ([OpenAI][1]).

## 4) Provide Rich Context
- Include:
  - Code snippets
  - Stack traces with paths
  - Configs & tests
  - Known patterns/style
- Codex performs best when context is explicit ([Gist][2]).

## 5) Test-Anchored Development
- Always anchor changes to failing tests:
  - Write the test that should fail
  - Ask Codex to fix it
  - Run tests
  - Review results
- Tests are the success metric ([OpenAI][1]).

## 6) Limit Autonomy & Approvals
- In CLI tools:
  - Use sandbox restrictions
  - Use approval gates for risky actions
  - Prefer workspace-write over full autonomy
- This prevents accidental file or system changes ([GitHub][3]).

## 7) Explain Diffs
- Always request:
  - “Explain the diff and why it’s correct.”
- Before merging or committing, require justification.

## 8) Parallel Tasks & Backlog
- You can queue multiple tasks at once.
- Codex will run each in isolated environments; results are reviewed in order ([Gist][2]).

## 9) Verify & Validate
- Never trust blindly:
  - Manual code review
  - Run CI/tests
  - Check integration with real workflows
- Codex outputs should be verified like human contributions ([OpenAI][1]).

## 10) Learn & Improve
- Track:
  - Failed prompts
  - Wrong assumptions
  - Successful patterns
- Logging helps improve future runs and prompt refinement ([Gist][2]).

## Quick Prompt Patterns
- Plan prompt:
  - “Plan steps to implement feature X with tests, edge cases, and benchmarks.”
- Fix prompt:
  - “Fix tests in `tests/test_x.py` and explain the changes.”
- Review prompt:
  - “Review this diff and point out logic or coverage issues.”

## Key Principles (Lightning)
- Codex works best with structure + context + measurable outcomes ([OpenAI][1]).
- Think in issues/tasks, not freeform chat ([OpenAI][1]).
- Small, verified steps > big monolithic requests ([Gist][2]).
