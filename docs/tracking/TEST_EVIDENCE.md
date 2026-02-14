# Test Evidence Log

Record verification for each change/bug fix.
Newest entries go first.

## Entry Template
- `Evidence ID:` TST-YYYYMMDD-###
- `Date:`
- `Owner/Role:`
- `Related change:` CHG-...
- `Related bug:` BUG-... (optional)
- `Scope:`
- `Test type:` Unit | Integration | E2E | Manual | Smoke
- `Command or procedure:`
- `Result:` Pass | Fail | Partial
- `Notes:`
- `Artifacts:` screenshots/logs/report files

---

## TST-20260214-007
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260214-007
- `Related bug:` BUG-20260214-004
- `Scope:` Queue preflight checks and backend dispatch behavior
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` `22 passed in 5.21s`.
- `Artifacts:` pytest console output

## TST-20260214-006
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260214-006
- `Related bug:` BUG-20260214-003
- `Scope:` Admin cache/query/config/routing hardening
- `Test type:` Manual
- `Command or procedure:` Compiled changed modules and validated targeted symbol/text updates with search checks.
- `Result:` Pass
- `Notes:` Behavior-only hardening; no API contract changes.
- `Artifacts:` N/A

## TST-20260214-005
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260214-005
- `Related bug:` None
- `Scope:` `gh` CLI ruleset setup documentation
- `Test type:` Manual
- `Command or procedure:` Reviewed command arguments and check names for consistency with documented required statuses.
- `Result:` Pass
- `Notes:` Command is intended as a starter template; owner/repo variables are configurable.
- `Artifacts:` `docs/tracking/CI_ENFORCEMENT.md`

## TST-20260214-004
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260214-004
- `Related bug:` None
- `Scope:` Branch protection guidance document
- `Test type:` Manual
- `Command or procedure:` Cross-checked documented required check names against workflow/job names in `.github/workflows`.
- `Result:` Pass
- `Notes:` Ready to apply via GitHub branch protection UI.
- `Artifacts:` `docs/tracking/CI_ENFORCEMENT.md`

## TST-20260214-003
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260214-003
- `Related bug:` None
- `Scope:` CI enforcement of PR tracking IDs
- `Test type:` Manual
- `Command or procedure:` Reviewed regex requirements against `.github/pull_request_template.md` fields and verified workflow syntax.
- `Result:` Pass
- `Notes:` Check triggers on PR open/edit/reopen/synchronize targeting `main`.
- `Artifacts:` `.github/workflows/pr-tracking-check.yml`

## TST-20260214-002
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260214-002
- `Related bug:` BUG-20260214-002
- `Scope:` Unused symbol cleanup + PR process enforcement template
- `Test type:` Manual
- `Command or procedure:` Verified files compile structurally and removed symbols no longer exist via `Select-String` checks.
- `Result:` Pass
- `Notes:` No runtime behavior changes expected; cleanup-only.
- `Artifacts:` N/A

## TST-20260214-001
- `Date:` 2026-02-14
- `Owner/Role:` Documentation System
- `Related change:` CHG-20260214-001
- `Related bug:` None
- `Scope:` Documentation structure creation
- `Test type:` Manual
- `Command or procedure:` Verified file creation and README links.
- `Result:` Pass
- `Notes:` Process docs are now available for team use.
- `Artifacts:` N/A
