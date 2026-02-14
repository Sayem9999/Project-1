# Project Tracking System

This project now uses a structured change-tracking workflow.

## Goals
- Track every meaningful change.
- Record why a change was made (not just what changed).
- Keep a permanent bug register with status and root cause.
- Keep test evidence tied to each change.
- Support role-based collaboration (frontend, backend, analyst, UI tester, etc.).

## Folder Structure
- `docs/tracking/CHANGE_LOG.md`: Chronological log of merged changes.
- `docs/tracking/BUG_REGISTER.md`: Source of truth for bugs and incidents.
- `docs/tracking/DECISION_LOG.md`: Engineering decisions and tradeoffs.
- `docs/tracking/TEST_EVIDENCE.md`: Verification and QA outcomes.
- `docs/tracking/WORK_ITEMS.md`: Active and planned work.
- `docs/tracking/templates/`: Templates for consistent entries.
- `docs/MULTI_AGENT_WORKFLOW.md`: Role-based execution model.

## Rules (From Now On)
1. All new tasks must start in `docs/tracking/WORK_ITEMS.md` first.
2. Every code change gets a `CHANGE_LOG` entry.
3. Every bug gets a `BUG_REGISTER` entry, even if fixed quickly.
4. Every non-trivial technical tradeoff gets a `DECISION_LOG` entry.
5. Every shipped/fixed item includes test evidence in `TEST_EVIDENCE`.
6. Each entry should include:
   - Date
   - Owner/role
   - Files changed
   - Reason ("why")
   - Risk
   - Validation done

## Entry Order
Add new entries at the top of each file (newest first).
