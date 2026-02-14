# Change Log

Use this file for merged or completed changes.
Newest entries go first.

## Entry Template
- `Change ID:` CHG-YYYYMMDD-###
- `Date:`
- `Owner/Role:` (Backend Developer / Frontend Developer / Analyst / UI Tester / etc.)
- `Summary:`
- `Why this change was needed:`
- `Files changed:`
- `Risk level:` Low | Medium | High
- `Linked bug(s):` BUG-... (if applicable)
- `Validation:` tests/manual checks run
- `Rollback plan:`

---

## CHG-20260214-007
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Summary:` Added production queue preflight checks and fixed dispatch import path in jobs router.
- `Why this change was needed:` Backend tests required explicit 503 failure modes for missing workers/queue consumers and stable dispatch path behavior.
- `Files changed:`
  - `backend/app/routers/jobs.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260214-004
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` from `backend` passed.
- `Rollback plan:` Revert this commit to restore previous queue behavior.

## CHG-20260214-006
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Summary:` Hardened cache/query behavior and removed privileged config default.
- `Why this change was needed:` Follow-up hardening for reliability and security posture in actively edited backend modules.
- `Files changed:`
  - `backend/app/services/admin_cache.py`
  - `backend/app/agents/routing_policy.py`
  - `backend/app/config.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260214-003
- `Validation:` Python compile check + static grep checks.
- `Rollback plan:` Revert this commit if unexpected behavior is observed in startup/admin health.

## CHG-20260214-005
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Summary:` Added a short `gh` CLI command block to automate branch ruleset setup.
- `Why this change was needed:` Requested automation guidance instead of UI-only steps for faster and repeatable enforcement setup.
- `Files changed:`
  - `docs/tracking/CI_ENFORCEMENT.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` None
- `Validation:` Verified command block includes required status check contexts documented in the same file.
- `Rollback plan:` Remove CLI section if GitHub API contract changes.

## CHG-20260214-004
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Summary:` Added branch protection guidance for enforcing required PR checks on `main`.
- `Why this change was needed:` Requested explicit setup guidance to activate CI and tracking governance in GitHub settings.
- `Files changed:`
  - `docs/tracking/CI_ENFORCEMENT.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` None
- `Validation:` Verified required check names match existing workflow job names.
- `Rollback plan:` Remove `docs/tracking/CI_ENFORCEMENT.md` if policy changes.

## CHG-20260214-003
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Summary:` Added CI workflow to enforce required tracking IDs in PR body.
- `Why this change was needed:` Requested automatic enforcement so PRs fail when tracking references are missing.
- `Files changed:`
  - `.github/workflows/pr-tracking-check.yml`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` None
- `Validation:` Workflow YAML structure reviewed and regex rules verified against PR template fields.
- `Rollback plan:` Remove `.github/workflows/pr-tracking-check.yml` if enforcement needs to be temporarily disabled.

## CHG-20260214-002
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Summary:` Removed unused backend symbols and added PR template to enforce tracking workflow.
- `Why this change was needed:` Requested cleanup of maintenance noise and enforcement of WORK/BUG/CHG/TST documentation on every PR.
- `Files changed:`
  - `backend/app/routers/admin.py`
  - `backend/app/agents/routing_policy.py`
  - `.github/pull_request_template.md`
  - `docs/TRACKING_SYSTEM.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260214-002
- `Validation:` Manual review + static grep checks for removed symbols.
- `Rollback plan:` Revert this change set and restore removed symbols/template file.

## CHG-20260214-001
- `Date:` 2026-02-14
- `Owner/Role:` Documentation System
- `Summary:` Introduced mandatory tracking system and multi-agent workflow docs.
- `Why this change was needed:` Team requested full traceability for all changes, especially bug fixes.
- `Files changed:`
  - `docs/TRACKING_SYSTEM.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/DECISION_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/templates/change_entry.md`
  - `docs/tracking/templates/bug_entry.md`
  - `docs/tracking/templates/decision_entry.md`
  - `docs/tracking/templates/test_evidence_entry.md`
  - `docs/MULTI_AGENT_WORKFLOW.md`
  - `README.md`
- `Risk level:` Low
- `Linked bug(s):` None
- `Validation:` File structure created and linked from README.
- `Rollback plan:` Remove tracking docs and README links if workflow is rejected.
