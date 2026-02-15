# Branch Protection Guidance

Use this for `main` branch protection in GitHub.

## Goal
Prevent merges unless required quality and tracking checks pass.

## Required Status Checks
Mark these checks as **required** in branch protection:
- `Enforce Tracking IDs In PR Body`
- `Lint & Type Check`
- `Backend Pytest`
- `Orchestration Callback Security`
- `Stage Timeout Regression`
- `Migration Check`
- `Security Scan`
- `Frontend Lint`

Recommended (optional but useful):
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

## GitHub CLI (Quick Setup)
Use this to create a ruleset from CLI.

```bash
OWNER="Sayem9999"
REPO="Project-1"

gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO/rulesets" \
  -f name="main-protection" \
  -f target="branch" \
  -f enforcement="active" \
  -f conditions[ref_name][include][]=refs/heads/main \
  -f rules[][type]=pull_request \
  -f rules[][parameters][required_approving_review_count]=1 \
  -f rules[][parameters][require_code_owner_review]=false \
  -f rules[][type]=required_status_checks \
  -f rules[][parameters][strict_required_status_checks_policy]=true \
  -f rules[][parameters][required_status_checks][][context]="Enforce Tracking IDs In PR Body" \
  -f rules[][parameters][required_status_checks][][context]="Lint & Type Check" \
  -f rules[][parameters][required_status_checks][][context]="Backend Pytest" \
  -f rules[][parameters][required_status_checks][][context]="Orchestration Callback Security" \
  -f rules[][parameters][required_status_checks][][context]="Stage Timeout Regression" \
  -f rules[][parameters][required_status_checks][][context]="Migration Check" \
  -f rules[][parameters][required_status_checks][][context]="Security Scan" \
  -f rules[][parameters][required_status_checks][][context]="Frontend Lint"
```

Notes:
- Run `gh auth login` first.
- If branch protection already exists, update/remove old rule before applying.

## Enforcement Notes
- The PR template and `PR Tracking Enforcement` workflow work together.
- If a PR body omits `WRK`, `CHG`, `TST` (and `BUG`/`DEC` as `N/A` or ID), merge will be blocked.

## Team Process
- Open/assign work in `docs/tracking/WORK_ITEMS.md` first.
- Keep `CHANGE_LOG`, `BUG_REGISTER`, and `TEST_EVIDENCE` in sync before requesting review.
