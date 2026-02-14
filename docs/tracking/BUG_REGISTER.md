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

## BUG-20260215-003
- `Title:` Backend lacked an executable deployment preflight and live-start verification path
- `Date reported:` 2026-02-15
- `Reported by:` Codex deploy pass
- `Owner:` Backend Developer
- `Severity:` S3
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Deployment success depended on manual assumptions; no single preflight signal existed to confirm ffmpeg/db/redis/llm/n8n consistency before startup.
- `Expected behavior:` A pre-deploy check should deterministically report readiness, and deployment verification should include live endpoint checks.
- `Root cause:` Operational tooling was fragmented across scripts without a dedicated readiness gate.
- `Fix summary:` Added `readiness_check.py`, `make ready`, updated env template + readiness docs, hardened ffmpeg runtime fallback paths, and verified live `/health` and `/ready` after startup.
- `Files changed:`
  - `backend/.env.example`
  - `backend/Makefile`
  - `backend/docs/READINESS.md`
  - `backend/scripts/readiness_check.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/services/rendering_orchestrator.py`
  - `backend/tests/test_parallel_render.py`
- `Validation evidence:` TST-20260215-003
- `Regression risk:` Low
- `Linked change:` CHG-20260215-003

## BUG-20260215-002
- `Title:` Backend readiness depended on missing ffmpeg binaries and outdated env template keys
- `Date reported:` 2026-02-15
- `Reported by:` Codex readiness run
- `Owner:` Backend Developer
- `Severity:` S2
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Readiness failed when ffmpeg was not on PATH, `.env.example` still referenced obsolete `N8N_WEBHOOK_URL`, and no one-command preflight existed.
- `Expected behavior:` Backend should have a current env template and a deterministic readiness check that validates core runtime dependencies.
- `Root cause:` Migration away from repo-shipped ffmpeg artifacts left runtime assumptions partially coupled to PATH.
- `Fix summary:` Added readiness script + Makefile target + readiness doc; updated env template for n8n keys; added `imageio_ffmpeg` fallback in runtime ffmpeg resolution; made parallel-render test duration check resilient without ffprobe.
- `Files changed:`
  - `backend/.env.example`
  - `backend/scripts/readiness_check.py`
  - `backend/Makefile`
  - `backend/docs/READINESS.md`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/services/rendering_orchestrator.py`
  - `backend/tests/test_parallel_render.py`
- `Validation evidence:` TST-20260215-002
- `Regression risk:` Low
- `Linked change:` CHG-20260215-002

## BUG-20260215-001
- `Title:` Workflow runtime could fail due to unresolved ffmpeg binary and undefined logger in orchestration path
- `Date reported:` 2026-02-15
- `Reported by:` Codex backend hardening pass
- `Owner:` Backend Developer
- `Severity:` S2
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Standard workflow used bare `ffmpeg` commands and could fail when ffmpeg was not on PATH; orchestrated render failure path referenced `logger` without definition.
- `Expected behavior:` Workflow should use bundled ffmpeg when available and log orchestration errors without NameError.
- `Root cause:` Tool path resolution not reused in workflow engine and missing logger initialization in module scope.
- `Fix summary:` Added `_resolve_tool_path(...)` and replaced bare `ffmpeg` calls in GPU detection/thumbnail extraction; added `structlog` logger setup.
- `Files changed:`
  - `backend/app/services/workflow_engine.py`
- `Validation evidence:` TST-20260215-001
- `Regression risk:` Low
- `Linked change:` CHG-20260215-001

## BUG-20260214-005
- `Title:` Missing outbound n8n webhook reliability controls and brittle ffmpeg test bootstrap
- `Date reported:` 2026-02-14
- `Reported by:` Codex implementation/test run
- `Owner:` Backend Developer
- `Severity:` S2
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` No dedicated n8n outbound client/signature/retry logic existed, and backend suite could fail on systems where `ffmpeg` was not on PATH.
- `Expected behavior:` Terminal job updates should notify n8n using signed requests with timeout/retry, and tests should resolve bundled ffmpeg binaries when PATH is missing.
- `Root cause:` Integration gap for outbound n8n events and test dependency on environment-specific PATH setup.
- `Fix summary:` Added n8n settings + resilient webhook client + terminal status trigger in workflow updates; updated parallel render test to locate bundled ffmpeg/ffprobe.
- `Files changed:`
  - `backend/app/config.py`
  - `backend/app/services/n8n_service.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/tests/test_n8n_service.py`
  - `backend/tests/test_parallel_render.py`
- `Validation evidence:` TST-20260214-008
- `Regression risk:` Low
- `Linked change:` CHG-20260214-008

## BUG-20260214-004
- `Title:` Production queue dispatch path lacked deterministic preflight guards
- `Date reported:` 2026-02-14
- `Reported by:` Codex test run
- `Owner:` Backend Developer
- `Severity:` S2
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` `enqueue_job` returned generic dispatch failures when no workers or no queue subscribers existed; dispatch path also relied on late `asyncio` import.
- `Expected behavior:` Production path should fail early with actionable 503 details for worker visibility and queue subscription.
- `Root cause:` Missing explicit preflight checks against Celery diagnostics and late import placement.
- `Fix summary:` Added production diagnostics checks for worker count and queue consumer presence; moved `asyncio` import to module level.
- `Files changed:`
  - `backend/app/routers/jobs.py`
  - `docs/tracking/WORK_ITEMS.md`
  - `docs/tracking/BUG_REGISTER.md`
  - `docs/tracking/CHANGE_LOG.md`
  - `docs/tracking/TEST_EVIDENCE.md`
- `Validation evidence:` TST-20260214-007
- `Regression risk:` Low
- `Linked change:` CHG-20260214-007

## BUG-20260214-003
- `Title:` Risky bootstrap default and brittle cache health/query behavior
- `Date reported:` 2026-02-14
- `Reported by:` Codex review
- `Owner:` Backend Developer
- `Severity:` S3
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` `admin_cache` used `!= None` SQL comparison and had no overall timeout around concurrent health probes; routing circuit breaker kept stale reset timestamp; config had hardcoded bootstrap admin email default.
- `Expected behavior:` Robust SQL null checks/timeouts, clean breaker state reset, and no privileged email defaults in source code.
- `Root cause:` Incremental refactors left non-idiomatic query and permissive/risky defaults.
- `Fix summary:` Replaced with `isnot(None)`, wrapped health gather in `wait_for`, cleared `circuit_open_until` on reset, and set `admin_bootstrap_email` default to `None`.
- `Files changed:`
  - `backend/app/services/admin_cache.py`
  - `backend/app/agents/routing_policy.py`
  - `backend/app/config.py`
- `Validation evidence:` TST-20260214-006
- `Regression risk:` Low
- `Linked change:` CHG-20260214-006

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
