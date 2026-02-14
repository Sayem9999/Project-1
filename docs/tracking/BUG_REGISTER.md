# Bug Register

Use this file as the single source of truth for defects.
Newest entries go first.

## Status Values
- `Open`
- `Investigating`
- `In Progress`
- `Blocked`
- `Resolved`
- `Closed`

## Severity Values
- `S1` Critical
- `S2` High
- `S3` Medium
- `S4` Low

## Entry Template
- `Bug ID:` BUG-YYYYMMDD-###
- `Title:`
- `Date reported:`
- `Reported by:`
- `Owner:`
- `Severity:`
- `Status:`
- `Environment:` Local / Staging / Production
- `Symptoms:`
- `Expected behavior:`
- `Root cause:`
- `Fix summary:`
- `Files changed:`
- `Validation evidence:`
- `Regression risk:`
- `Linked change:` CHG-...

---

## BUG-20260214-002
- `Title:` Unused imports and stale cache placeholders in admin/routing modules
- `Date reported:` 2026-02-14
- `Reported by:` Codex review
- `Owner:` Backend Developer
- `Severity:` S4
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Static review showed unused imports and unused cache vars adding noise and confusion.
- `Expected behavior:` Modules should only contain actively used imports/variables.
- `Root cause:` Iterative refactors left stale symbols after logic moved to `admin_cache` service.
- `Fix summary:` Removed unused imports and removed unused cache placeholder vars.
- `Files changed:`
  - `backend/app/routers/admin.py`
  - `backend/app/agents/routing_policy.py`
- `Validation evidence:` TST-20260214-002
- `Regression risk:` Low
- `Linked change:` CHG-20260214-002

## BUG-20260214-001 (Placeholder)
- `Title:` No documented bug yet (placeholder to keep format visible)
- `Date reported:` 2026-02-14
- `Reported by:` System
- `Owner:` Unassigned
- `Severity:` S4
- `Status:` Closed
- `Environment:` N/A
- `Symptoms:` N/A
- `Expected behavior:` N/A
- `Root cause:` N/A
- `Fix summary:` Placeholder record only.
- `Files changed:` None
- `Validation evidence:` N/A
- `Regression risk:` Low
- `Linked change:` CHG-20260214-001
