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

## WRK-20260215-007
- `Title:` Implement Phase-A True Post-Production Depth foundations across timeline/audio/color/graphics pipelines
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` Moves roadmap from planning into executable post-production depth features used by real renders.
- `Scope / files:`
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
- `Dependencies:` Existing graph workflow + render orchestrator
- `Exit criteria:` Advanced transitions/speed/keyframe-aware rendering hooks, audio mastering filter chain, color pipeline defaults, subtitle styling/QA are integrated and tested.

## WRK-20260215-006
- `Title:` Narrow roadmap to only True Post-Production Depth scope
- `Status:` Done
- `Owner/Role:` Analyst + Backend Developer
- `Priority:` P1
- `Why this matters:` Product direction is now explicitly focused on deep post-production capabilities only.
- `Scope / files:`
  - `docs/STUDIO_ROADMAP.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` Existing roadmap document
- `Exit criteria:` Roadmap contains only timeline/audio/color/graphics depth tracks and related BE/FE tickets.

## WRK-20260215-005
- `Title:` Publish phased studio-replacement roadmap with backend/frontend ticket map
- `Status:` Done
- `Owner/Role:` Analyst + Backend Developer
- `Priority:` P1
- `Why this matters:` Team needs an execution plan to evolve from AI-assisted editing into a full studio replacement.
- `Scope / files:`
  - `docs/STUDIO_ROADMAP.md`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` Current architecture and known product gaps
- `Exit criteria:` Roadmap contains phased milestones (`MVP`, `Pro`, `Enterprise`) and BE/FE ticket mapping with acceptance gates.

## WRK-20260215-004
- `Title:` Enforce non-pass-through editing so AI output visibly differs from source footage
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` Users expect AI editing decisions, not source-identical outputs.
- `Scope / files:`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/graph/nodes/compiler.py`
  - `backend/tests/test_editing_cuts.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` Existing render orchestration and graph compiler pipeline
- `Exit criteria:` Empty/full-clip cut plans are converted into deterministic highlight cuts and tests pass.

## WRK-20260215-003
- `Title:` Finalize backend deployment readiness and verify live startup endpoints
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` Backend must be verifiably deployable with migrations applied, health endpoints reachable, and readiness checks passing.
- `Scope / files:`
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
- `Dependencies:` Existing backend `.venv`, alembic migrations, and runtime config in `.env`
- `Exit criteria:` readiness preflight passes, migrations are at head, tests pass, and `/health` + `/ready` return 200 on a live process.

## WRK-20260215-002
- `Title:` Add backend readiness preflight and make ffmpeg runtime resolution independent of PATH/bundled binaries
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` Backend should be launch-ready with a deterministic preflight and should still render when ffmpeg is not globally installed or repo-shipped.
- `Scope / files:`
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
- `Dependencies:` `imageio_ffmpeg` from existing dependency graph
- `Exit criteria:` `scripts/readiness_check.py` reports READY and backend test suite stays green.

## WRK-20260215-001
- `Title:` Remove runtime blockers in workflow engine so backend job processing reliably produces outputs
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` Jobs can fail at runtime when FFmpeg is not on PATH or when orchestration error logging hits undefined logger.
- `Scope / files:`
  - `backend/app/services/workflow_engine.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` Bundled ffmpeg binary under `tools/ffmpeg-8.0.1-essentials_build/bin`
- `Exit criteria:` Workflow uses resolved ffmpeg path and no runtime NameError in orchestration failure path.

## WRK-20260214-008
- `Title:` Integrate outbound n8n status webhook with retries/signature and protect pipeline from n8n outages
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` External orchestration needs reliable terminal-state notifications without risking job pipeline failures if n8n is unavailable.
- `Scope / files:`
  - `backend/app/config.py`
  - `backend/app/services/n8n_service.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/tests/test_n8n_service.py`
  - `backend/tests/test_parallel_render.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` Existing workflow `update_status(...)` terminal state updates
- `Exit criteria:` n8n config + signed client + trigger point + resilience tests are in place and backend suite is green.

## WRK-20260214-007
- `Title:` Stabilize backend queue preflight behavior and green test suite
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P1
- `Why this matters:` Production dispatch errors need deterministic diagnostics, and backend tests must stay green.
- `Scope / files:`
  - `backend/app/routers/jobs.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` Existing Celery diagnostics helper in jobs router
- `Exit criteria:` Queue preflight checks are explicit and `pytest` passes.

## WRK-20260214-006
- `Title:` Harden admin cache/query semantics and configuration defaults
- `Status:` Done
- `Owner/Role:` Backend Developer
- `Priority:` P2
- `Why this matters:` Prevents stale circuit state, avoids ambiguous SQL null checks, and removes risky default bootstrap behavior.
- `Scope / files:`
  - `backend/app/services/admin_cache.py`
  - `backend/app/agents/routing_policy.py`
  - `backend/app/config.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Dependencies:` None
- `Exit criteria:` Code updated and validated by compile/static checks with tracking entries linked.

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
