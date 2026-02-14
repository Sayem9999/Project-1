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

## TST-20260215-016
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-016
- `Related bug:` BUG-20260215-013
- `Scope:` `/api/jobs/{id}/start` must not hang; smoke E2E should progress past job start.
- `Test type:` Unit + Smoke
- `Command or procedure:` Run `backend` pytest `.\.venv\Scripts\python.exe -m pytest -q tests/test_jobs.py::test_start_job_returns_without_waiting_for_queue_dispatch`; run live smoke `backend\.venv\Scripts\python.exe ..\scripts\smoke_e2e.py` (repo root) against local API/worker.
- `Result:` Pass
- `Notes:` Unit regression passed; live smoke completed end-to-end. Smoke output: `tmp/smoke/download-59.mp4` (job `59`).
- `Artifacts:` `tmp/smoke/download-59.mp4`

## TST-20260215-017
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-017
- `Related bug:` BUG-20260215-014
- `Scope:` Smoke scripts input/FFmpeg resolution.
- `Test type:` Manual
- `Command or procedure:` Run `python scripts/smoke_test.py` and `python scripts/smoke_e2e.py` from repo root with local stack running.
- `Result:` Partial
- `Notes:` Smoke scripts no longer depend on hardcoded FFmpeg path or `frontend/dummy_video.mp4`. `smoke_test.py` can still time out if the AI pipeline stalls.
- `Artifacts:` console output

## TST-20260215-018
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-018
- `Related bug:` BUG-20260215-015
- `Scope:` LLM timeout bounding + SQLite lock hardening + smoke polling robustness.
- `Test type:` Smoke
- `Command or procedure:` Restart local API/worker; run `python scripts/smoke_e2e.py`.
- `Result:` Pass
- `Notes:` Smoke E2E completed end-to-end after changes. Output: `tmp/smoke/download-68.mp4`.
- `Artifacts:` `tmp/smoke/download-68.mp4`

## TST-20260215-015
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer + Frontend Developer
- `Related change:` CHG-20260215-015
- `Related bug:` BUG-20260215-012
- `Scope:` Migration deploy validation, smoke checks for requested endpoints, callback-security CI path, and autonomy action audit trail
- `Test type:` Integration
- `Command or procedure:` Run `ENVIRONMENT=production alembic upgrade head`; run `pytest -q tests/test_jobs.py tests/test_orchestration_callback_security.py tests/test_maintenance_autonomy_api.py`; run full `pytest -q`; run `npm run lint`.
- `Result:` Pass
- `Notes:` Migration applied `e4f7b7ad4f62 -> 7c1d2e8f4a91`; targeted suite `13 passed`; full backend `51 passed`; frontend lint passed with two pre-existing warnings in unrelated files.
- `Artifacts:` alembic + pytest + lint console output

## TST-20260215-014
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer + Frontend Developer
- `Related change:` CHG-20260215-014
- `Related bug:` BUG-20260215-011
- `Scope:` Autonomy profile tuning logic and admin UI control panel integration
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q tests/test_autonomy_service.py` and full backend `.\.venv\Scripts\python.exe -m pytest -q`; run `npm run lint` in `frontend`.
- `Result:` Pass
- `Notes:` Autonomy tests `8 passed`; backend suite `49 passed in 9.60s`; frontend lint passed with existing hook-dependency warnings unrelated to this panel.
- `Artifacts:` pytest + frontend lint console output

## TST-20260215-013
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-013
- `Related bug:` BUG-20260215-010
- `Scope:` OpenAI-first provider routing config and fallback model-loop fix
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` `45 passed in 10.38s`.
- `Artifacts:` pytest console output

## TST-20260215-012
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-012
- `Related bug:` BUG-20260215-009
- `Scope:` Orchestration callback signature/replay security and end-to-end API behavior
- `Test type:` Integration
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q tests/test_orchestration_callback_security.py tests/test_n8n_service.py tests/test_jobs.py`, then run full `.\.venv\Scripts\python.exe -m pytest -q`.
- `Result:` Pass
- `Notes:` Targeted run: `15 passed`; full backend run: `45 passed in 9.62s`.
- `Artifacts:` pytest console output

## TST-20260215-011
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-011
- `Related bug:` BUG-20260215-008
- `Scope:` Pending post-settings schema/router/workflow/migration hardening
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`, then run `.\.venv\Scripts\python.exe -m alembic upgrade head`.
- `Result:` Pass
- `Notes:` `42 passed in 9.44s`; Alembic upgraded from `82ef48fc3c57` to `e4f7b7ad4f62`.
- `Artifacts:` pytest + alembic console output

## TST-20260215-010
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-010
- `Related bug:` BUG-20260215-007
- `Scope:` Idle autonomy self-heal/improve loop behavior
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` `40 passed in 8.60s`, including new `test_autonomy_service.py`.
- `Artifacts:` pytest console output

## TST-20260215-009
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-009
- `Related bug:` BUG-20260215-006
- `Scope:` OpenClaw strategy robustness, n8n payload/headers, workflow QA persistence semantics
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` `37 passed in 8.99s`, including new `test_openclaw_service.py` and extended `test_n8n_service.py`.
- `Artifacts:` pytest console output

## TST-20260215-008
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer + Frontend Developer
- `Related change:` CHG-20260215-008
- `Related bug:` BUG-20260215-005
- `Scope:` Post-depth payload plumbing and persistence validation
- `Test type:` Integration
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`; run `npm run lint` in `frontend`.
- `Result:` Pass
- `Notes:` Backend suite passed (`35 passed in 8.59s`) with new upload/edit persistence tests. Frontend lint passed with existing non-blocking hook dependency warnings.
- `Artifacts:` pytest console output + frontend lint output

## TST-20260215-007
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-007
- `Related bug:` None
- `Scope:` True Post-Production Depth foundational execution layer
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` `33 passed in 7.83s`, including new `test_post_production_depth.py`.
- `Artifacts:` pytest console output

## TST-20260215-006
- `Date:` 2026-02-15
- `Owner/Role:` Analyst + Backend Developer
- `Related change:` CHG-20260215-006
- `Related bug:` None
- `Scope:` Roadmap scope validation for True Post-Production Depth only
- `Test type:` Manual
- `Command or procedure:` Review `docs/STUDIO_ROADMAP.md` and verify it contains only timeline/audio/color/graphics depth workstreams.
- `Result:` Pass
- `Notes:` Broader MVP/Pro/Enterprise planning sections were removed by design.
- `Artifacts:` `docs/STUDIO_ROADMAP.md`

## TST-20260215-005
- `Date:` 2026-02-15
- `Owner/Role:` Analyst + Backend Developer
- `Related change:` CHG-20260215-005
- `Related bug:` None
- `Scope:` Roadmap documentation quality and ticket map completeness
- `Test type:` Manual
- `Command or procedure:` Review `docs/STUDIO_ROADMAP.md` for phased milestones (`MVP`, `Pro`, `Enterprise`), BE/FE ticket mapping, and measurable exit gates.
- `Result:` Pass
- `Notes:` Roadmap includes milestone gates, execution order, ownership model, and ticket-level acceptance criteria.
- `Artifacts:` `docs/STUDIO_ROADMAP.md`

## TST-20260215-004
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-004
- `Related bug:` BUG-20260215-004
- `Scope:` AI cut guardrails to prevent source-identical outputs
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` `29 passed in 8.26s`, including new `test_editing_cuts.py`.
- `Artifacts:` pytest console output

## TST-20260215-003
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-003
- `Related bug:` BUG-20260215-003
- `Scope:` Deployment readiness + live startup verification
- `Test type:` Integration
- `Command or procedure:` Run `.\.venv\Scripts\python.exe scripts\readiness_check.py`, `.\.venv\Scripts\python.exe -m alembic upgrade head`, `.\.venv\Scripts\python.exe -m pytest -q`, then start uvicorn and query `/health` + `/ready`.
- `Result:` Pass
- `Notes:` Readiness reported READY; migration applied; tests `26 passed`; live endpoint checks returned HTTP 200.
- `Artifacts:` console output from readiness/migration/pytest/live health checks

## TST-20260215-002
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-002
- `Related bug:` BUG-20260215-002
- `Scope:` Backend launch/readiness hardening and ffmpeg runtime fallback behavior
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe scripts\readiness_check.py` and `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` Readiness preflight reports READY; pytest result is `26 passed in 7.76s`.
- `Artifacts:` preflight console output + pytest console output

## TST-20260215-001
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260215-001
- `Related bug:` BUG-20260215-001
- `Scope:` Workflow engine runtime hardening (ffmpeg resolution + logger safety)
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` `26 passed in 6.53s`.
- `Artifacts:` pytest console output

## TST-20260214-008
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Related change:` CHG-20260214-008
- `Related bug:` BUG-20260214-005
- `Scope:` n8n outbound webhook client + terminal-state trigger + ffmpeg test bootstrap resilience
- `Test type:` Unit
- `Command or procedure:` Run `.\.venv\Scripts\python.exe -m pytest -q` in `backend`.
- `Result:` Pass
- `Notes:` `26 passed in 11.14s`, including new `test_n8n_service.py`.
- `Artifacts:` pytest console output

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
