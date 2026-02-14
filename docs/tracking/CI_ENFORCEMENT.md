# Branch Protection Guidance

Use this for `main` branch protection in GitHub.

## Goal
Prevent merges unless required quality and tracking checks pass.

## Required Status Checks
Mark these checks as **required** in branch protection:
- `Enforce Tracking IDs In PR Body`
- `Lint & Type Check`
- `Unit Tests`
- `Integration Tests`
- `Frontend Lint`

Recommended (optional but useful):
- `Migration Check`
- `Security Scan`
- `E2E Smoke Tests`

## GitHub Settings (UI)
1. Go to `Settings` -> `Branches` -> `Add branch ruleset` (or branch protection rule).
2. Branch name pattern: `main`.
3. Enable:
   - `Require a pull request before merging`
   - `Require status checks to pass before merging`
   - `Require branches to be up to date before merging`
4. Add required checks listed above.
5. Enable:
   - `Require conversation resolution before merging`
   - `Require signed commits` (if your team uses this)
   - `Do not allow bypassing the above settings` (recommended for strict governance)

## Enforcement Notes
- The PR template and `PR Tracking Enforcement` workflow work together.
- If a PR body omits `WRK`, `CHG`, `TST` (and `BUG`/`DEC` as `N/A` or ID), merge will be blocked.

## Team Process
- Open/assign work in `docs/tracking/WORK_ITEMS.md` first.
- Keep `CHANGE_LOG`, `BUG_REGISTER`, and `TEST_EVIDENCE` in sync before requesting review.

