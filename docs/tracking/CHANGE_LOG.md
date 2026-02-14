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

## CHG-20260215-014
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer + Frontend Developer
- `Summary:` Added autonomy workload profiles (`aggressive`/`conservative`) and an admin dashboard panel for live autonomy metrics/actions.
- `Why this change was needed:` You asked for tuning by hardware/workload and real-time admin control of autonomous behavior.
- `Files changed:`
  - `backend/app/services/autonomy_service.py`
  - `backend/app/routers/maintenance.py`
  - `backend/app/config.py`
  - `backend/.env.example`
  - `backend/tests/test_autonomy_service.py`
  - `frontend/components/admin/AutonomyPanel.tsx`
  - `frontend/app/admin/page.tsx`
  - `docs/ARCHITECTURE.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Medium
- `Linked bug(s):` BUG-20260215-011
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`49 passed`); `npm run lint` passed with pre-existing non-blocking warnings.
- `Rollback plan:` Set profile to conservative and stop using new panel/actions, or revert this commit.

## CHG-20260215-013
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Enabled OpenAI-first routing for self-improvement flows and fixed fallback provider model execution path.
- `Why this change was needed:` You requested Codex/OpenAI usage for self-improving behavior; fallback reliability issue had to be fixed to keep provider resilience.
- `Files changed:`
  - `backend/app/config.py`
  - `backend/app/agents/routing_policy.py`
  - `backend/app/agents/base.py`
  - `backend/.env`
  - `backend/.env.example`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260215-010
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`45 passed`).
- `Rollback plan:` Set `LLM_PRIMARY_PROVIDER` back to previous value or revert this commit.

## CHG-20260215-012
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Secured orchestration callback ingestion with HMAC signature checks, timestamp window validation, and replay protection.
- `Why this change was needed:` You requested secure callbacks and E2E-style orchestration tests; previous callback model relied on user auth and was replay-prone.
- `Files changed:`
  - `backend/app/routers/orchestration.py`
  - `backend/app/config.py`
  - `backend/.env.example`
  - `backend/tests/test_orchestration_callback_security.py`
  - `docs/ARCHITECTURE.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Medium
- `Linked bug(s):` BUG-20260215-009
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`45 passed`).
- `Rollback plan:` Revert this commit to restore prior auth-based callback behavior.

## CHG-20260215-011
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Hardened pending post-settings schema/router/workflow changes and validated migration path.
- `Why this change was needed:` You asked to finish pending backend schema/model/workflow/migration work from earlier phase with production-safe behavior.
- `Files changed:`
  - `backend/app/schemas.py`
  - `backend/app/routers/jobs.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/tests/test_jobs.py`
  - `backend/alembic/versions/e4f7b7ad4f62_add_post_depth_settings_and_qa_fields.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260215-008
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`42 passed`); `.\.venv\Scripts\python.exe -m alembic upgrade head` applied migration to head.
- `Rollback plan:` Revert this commit or disable strict validation paths if temporary compatibility rollback is needed.

## CHG-20260215-010
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Added idle autonomy loop for self-healing and self-improvement, with admin control endpoints and lifecycle management.
- `Why this change was needed:` You requested the webapp to self-improve/self-heal automatically when idle using available APIs.
- `Files changed:`
  - `backend/app/services/autonomy_service.py`
  - `backend/app/main.py`
  - `backend/app/routers/maintenance.py`
  - `backend/app/config.py`
  - `backend/.env.example`
  - `backend/tests/test_autonomy_service.py`
  - `docs/ARCHITECTURE.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Medium
- `Linked bug(s):` BUG-20260215-007
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`40 passed`).
- `Rollback plan:` Disable via `AUTONOMY_ENABLED=false` or revert this commit to remove idle automation behavior.

## CHG-20260215-009
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Hardened OpenClaw orchestration, n8n event delivery contract, workflow QA persistence semantics, and render orchestrator edge-case handling.
- `Why this change was needed:` You requested focused improvements across clawbot/n8n/workflow/architecture/orchestrator reliability.
- `Files changed:`
  - `backend/app/services/openclaw_service.py`
  - `backend/app/services/n8n_service.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/services/rendering_orchestrator.py`
  - `backend/tests/test_openclaw_service.py`
  - `backend/tests/test_n8n_service.py`
  - `docs/ARCHITECTURE.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260215-006
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`37 passed`).
- `Rollback plan:` Revert this commit to restore previous OpenClaw/n8n/workflow/orchestrator behavior.

## CHG-20260215-008
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer + Frontend Developer
- `Summary:` Completed post-depth settings flow from frontend controls to backend persistence with integration coverage.
- `Why this change was needed:` Post-production depth options existed in backend API but were not fully controllable from UI or validated by persistence tests.
- `Files changed:`
  - `frontend/app/dashboard/upload/page.tsx`
  - `frontend/app/jobs/[id]/JobPageClient.tsx`
  - `backend/tests/test_jobs.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260215-005
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`35 passed`), `npm run lint` passed with non-blocking warnings.
- `Rollback plan:` Revert this commit to restore prior UI forms and remove post-settings persistence tests.

## CHG-20260215-007
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Implemented initial True Post-Production Depth execution layer (timeline/render/audio/color/graphics hooks).
- `Why this change was needed:` You requested active work on deep post-production capabilities rather than high-level planning only.
- `Files changed:`
  - `backend/app/services/post_production_depth.py`
  - `backend/app/services/rendering_orchestrator.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/graph/nodes/audio.py`
  - `backend/app/graph/nodes/visuals.py`
  - `backend/app/graph/nodes/subtitle.py`
  - `backend/app/graph/nodes/compiler.py`
  - `backend/app/graph/state.py`
  - `backend/tests/test_post_production_depth.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Medium
- `Linked bug(s):` None
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`33 passed`).
- `Rollback plan:` Revert this commit to return to prior simpler render/audio/color/subtitle behavior.

## CHG-20260215-006
- `Date:` 2026-02-15
- `Owner/Role:` Analyst + Backend Developer
- `Summary:` Reduced studio roadmap scope to only True Post-Production Depth capabilities.
- `Why this change was needed:` You requested keeping only timeline/audio/color/graphics depth and removing broader MVP/Enterprise scope.
- `Files changed:`
  - `docs/STUDIO_ROADMAP.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` None
- `Validation:` Manual review confirmed roadmap now contains only the requested post-production depth tracks.
- `Rollback plan:` Restore prior roadmap version if broader planning scope is needed again.

## CHG-20260215-005
- `Date:` 2026-02-15
- `Owner/Role:` Analyst + Backend Developer
- `Summary:` Added a concrete phased roadmap for replacing a pro editing studio, including backend/frontend ticket mapping and acceptance gates.
- `Why this change was needed:` You requested a concrete execution plan with phased milestones and explicit BE/FE work breakdown.
- `Files changed:`
  - `docs/STUDIO_ROADMAP.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` None
- `Validation:` Manual review for milestone completeness, ticket coverage, and acceptance-criteria clarity.
- `Rollback plan:` Remove `docs/STUDIO_ROADMAP.md` and tracking entries if roadmap direction changes.

## CHG-20260215-004
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Added anti-pass-through edit policy so AI outputs are visibly edited instead of source-identical when cut plans are weak.
- `Why this change was needed:` You reported videos were identical to input; this enforces meaningful edits even when upstream agent output is empty/full-span.
- `Files changed:`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/graph/nodes/compiler.py`
  - `backend/tests/test_editing_cuts.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Medium
- `Linked bug(s):` BUG-20260215-004
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` passed (`29 passed`).
- `Rollback plan:` Revert this commit to restore prior cut-selection behavior.

## CHG-20260215-003
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Executed deployment hardening and verified a live backend start with passing health/ready checks.
- `Why this change was needed:` You requested to continue fixing/improving and deploy; this closes operational gaps so backend can be started and validated reliably.
- `Files changed:`
  - `backend/.env.example`
  - `backend/Makefile`
  - `backend/docs/READINESS.md`
  - `backend/scripts/readiness_check.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/services/rendering_orchestrator.py`
  - `backend/tests/test_parallel_render.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260215-003
- `Validation:` readiness script passed; alembic upgraded to head; pytest passed (`26 passed`); live server returned HTTP 200 for `/health` and `/ready`.
- `Rollback plan:` Revert this commit to restore previous startup/readiness workflow.

## CHG-20260215-002
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Added backend readiness tooling and hardened ffmpeg runtime resolution so backend can start and render reliably in local environments.
- `Why this change was needed:` You requested the backend be ready to produce results; readiness failed due to ffmpeg assumptions and outdated n8n env template keys.
- `Files changed:`
  - `backend/.env.example`
  - `backend/scripts/readiness_check.py`
  - `backend/Makefile`
  - `backend/docs/READINESS.md`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/services/rendering_orchestrator.py`
  - `backend/tests/test_parallel_render.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260215-002
- `Validation:` `.\.venv\Scripts\python.exe scripts\readiness_check.py` passed and `.\.venv\Scripts\python.exe -m pytest -q` passed (`26 passed`).
- `Rollback plan:` Revert this commit to return to previous startup/readiness behavior.

## CHG-20260215-001
- `Date:` 2026-02-15
- `Owner/Role:` Backend Developer
- `Summary:` Hardened workflow runtime path resolution and orchestration error logging to improve real job completion reliability.
- `Why this change was needed:` Backend should produce outputs consistently even when ffmpeg is not globally installed, and failure logging must never crash.
- `Files changed:`
  - `backend/app/services/workflow_engine.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260215-001
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` from `backend` passed (`26 passed`).
- `Rollback plan:` Revert this commit if tool path resolution causes unexpected deployment-specific behavior.

## CHG-20260214-008
- `Date:` 2026-02-14
- `Owner/Role:` Backend Developer
- `Summary:` Added outbound n8n webhook integration with retries/signature and made backend tests resilient when n8n/ffmpeg environment dependencies are missing.
- `Why this change was needed:` Requested n8n integration for terminal job states plus tests that prove the backend remains stable even when n8n is down.
- `Files changed:`
  - `backend/app/config.py`
  - `backend/app/services/n8n_service.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/tests/test_n8n_service.py`
  - `backend/tests/test_parallel_render.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Risk level:` Low
- `Linked bug(s):` BUG-20260214-005
- `Validation:` `.\.venv\Scripts\python.exe -m pytest -q` from `backend` passed (`26 passed`).
- `Rollback plan:` Revert this commit to disable outbound n8n notifications and restore previous test behavior.

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
