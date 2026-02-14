# Work Items

Track planned and active work. Move completed items into `CHANGE_LOG.md`.

## Status Values
- `Todo`
- `In Progress`
- `Blocked`
- `Done`

## Template
- `Work ID:` WRK-YYYYMMDD-###
- `Title:`
- `Status:`
- `Owner/Role:`
- `Priority:` P1 | P2 | P3
- `Why this matters:`
- `Scope / files:`
- `Dependencies:`
- `Exit criteria:`

---

## WRK-20260214-005
- `Title:` Add `gh` CLI automation block for branch ruleset setup
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P2
- `Why this matters:` Reduces manual setup errors and speeds branch protection rollout.
- `Scope / files:`
  - `docs/tracking/CI_ENFORCEMENT.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` GitHub CLI (`gh`) authentication
- `Exit criteria:` Document includes runnable CLI block with required status checks.

## WRK-20260214-004
- `Title:` Add branch protection and required-check guidance
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` Makes CI/tracking enforcement operational at repository settings level.
- `Scope / files:`
  - `docs/tracking/CI_ENFORCEMENT.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` Existing workflows and PR template
- `Exit criteria:` Clear instructions exist for required checks and branch protection config.

## WRK-20260214-003
- `Title:` Add CI enforcement for tracking IDs in PR body
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` Prevents undocumented PRs from merging without required tracking references.
- `Scope / files:`
  - `.github/workflows/pr-tracking-check.yml`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` `.github/pull_request_template.md` fields
- `Exit criteria:` PR check fails when tracking IDs are missing/invalid in PR body.

## WRK-20260214-002
- `Title:` Remove unused backend imports/cache vars and enforce tracking via PR template
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P2
- `Why this matters:` Reduces maintenance noise and enforces documentation discipline on future PRs.
- `Scope / files:`
  - `backend/app/routers/admin.py`
  - `backend/app/agents/routing_policy.py`
  - `.github/pull_request_template.md`
  - `docs/TRACKING_SYSTEM.md`
  - `docs/tracking/*`
- `Dependencies:` None
- `Exit criteria:` Code noise removed, PR template added, and tracking entries created (`BUG` + `CHG` + `TST`).

## WRK-20260214-001
- `Title:` Roll out tracking discipline across all future changes
- `Status:` In Progress
- `Owner/Role:` Team-wide
- `Priority:` P1
- `Why this matters:` Prevent undocumented fixes and lost bug context.
- `Scope / files:` All features, bug fixes, and releases.
- `Dependencies:` Team adoption.
- `Exit criteria:` Every new change includes entries in logs/templates.
