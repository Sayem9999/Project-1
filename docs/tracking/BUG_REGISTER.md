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

## BUG-20260215-011
- `Title:` Autonomy loop lacked workload profile controls and live operational visibility in admin UI
- `Date reported:` 2026-02-15
- `Reported by:` User request + Codex review
- `Owner:` Backend Developer + Frontend Developer
- `Severity:` S3
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Autonomy cadence was static, not tunable for hardware/workload; admin users could not see runtime load/metrics or trigger targeted autonomy actions from UI.
- `Expected behavior:` Operators can switch between conservative/aggressive modes and inspect live autonomy metrics/actions in the dashboard.
- `Root cause:` Initial autonomy implementation had fixed policy parameters and API-only visibility with no dedicated UI.
- `Fix summary:` Added profile presets, config-backed default mode, load guard metrics/counters, profile-switch API, and new admin autonomy panel with live polling and action controls.
- `Files changed:`
  - `backend/app/services/autonomy_service.py`
  - `backend/app/routers/maintenance.py`
  - `backend/app/config.py`
  - `backend/.env.example`
  - `backend/tests/test_autonomy_service.py`
  - `frontend/components/admin/AutonomyPanel.tsx`
  - `frontend/app/admin/page.tsx`
- `Validation evidence:` TST-20260215-014
- `Regression risk:` Low
- `Linked change:` CHG-20260215-014

## BUG-20260215-010
- `Title:` Agent fallback provider path skipped fallback model attempts due to unreachable loop block
- `Date reported:` 2026-02-15
- `Reported by:` Codex review
- `Owner:` Backend Developer
- `Severity:` S2
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` If primary provider failed, fallback providers could be selected but their model attempts were never executed, causing premature "all attempts failed" errors.
- `Expected behavior:` Fallback provider loop should iterate through each fallback provider model and attempt calls.
- `Root cause:` Incorrect indentation placed fallback `try` block under `if not fallback_config: continue`.
- `Fix summary:` Rebuilt fallback loop to explicitly iterate `for model in fallback_config.models` with proper error handling and retry sleep.
- `Files changed:`
  - `backend/app/agents/base.py`
  - `backend/app/agents/routing_policy.py`
  - `backend/app/config.py`
  - `backend/.env`
  - `backend/.env.example`
- `Validation evidence:` TST-20260215-013
- `Regression risk:` Low
- `Linked change:` CHG-20260215-013

## BUG-20260215-009
- `Title:` Orchestration callback endpoint lacked cryptographic verification and replay defenses
- `Date reported:` 2026-02-15
- `Reported by:` User request + Codex security review
- `Owner:` Backend Developer
- `Severity:` S2
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Callback accepted authenticated user payloads without webhook signature verification and had no replay-id dedupe for repeated event submissions.
- `Expected behavior:` Callback should accept only signed webhook requests and reject replays of the same event id.
- `Root cause:` Endpoint was designed as user-auth API action rather than service-to-service webhook contract.
- `Fix summary:` Added HMAC signature verification, timestamp tolerance checks, event-id replay protection using `processed_webhooks`, and callback security integration tests.
- `Files changed:`
  - `backend/app/routers/orchestration.py`
  - `backend/app/config.py`
  - `backend/.env.example`
  - `backend/tests/test_orchestration_callback_security.py`
- `Validation evidence:` TST-20260215-012
- `Regression risk:` Low
- `Linked change:` CHG-20260215-012

## BUG-20260215-008
- `Title:` Post-depth settings accepted invalid values that could degrade workflow behavior
- `Date reported:` 2026-02-15
- `Reported by:` Codex pending-change hardening pass
- `Owner:` Backend Developer
- `Severity:` S3
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Upload/edit payloads could carry unsupported transition/speed/subtitle/color values or out-of-range numeric values.
- `Expected behavior:` Settings should be validated/normalized at API boundary and safely bounded in workflow runtime.
- `Root cause:` Form-driven upload path had no explicit normalization, and workflow converted numeric settings without bounds.
- `Fix summary:` Added schema-level edit validation, upload/edit normalization helper in jobs router, bounded float coercion in workflow, and regression tests.
- `Files changed:`
  - `backend/app/schemas.py`
  - `backend/app/routers/jobs.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/tests/test_jobs.py`
- `Validation evidence:` TST-20260215-011
- `Regression risk:` Low
- `Linked change:` CHG-20260215-011

## BUG-20260215-007
- `Title:` System lacked idle-time autonomous self-heal/self-improve execution path
- `Date reported:` 2026-02-15
- `Reported by:` User request + Codex review
- `Owner:` Backend Developer
- `Severity:` S3
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Maintenance and health APIs existed but no always-on idle orchestrator invoked them automatically.
- `Expected behavior:` While idle, system should continuously execute safe healing and improvement tasks without disrupting active jobs.
- `Root cause:` No lifecycle-managed background controller connected maintenance/integration/cleanup/routing APIs under idle gating.
- `Fix summary:` Added `AutonomyService` idle loop, startup/shutdown wiring, admin endpoints for status/manual run, env/config knobs, and tests.
- `Files changed:`
  - `backend/app/services/autonomy_service.py`
  - `backend/app/main.py`
  - `backend/app/routers/maintenance.py`
  - `backend/app/config.py`
  - `backend/.env.example`
  - `backend/tests/test_autonomy_service.py`
  - `docs/ARCHITECTURE.md`
- `Validation evidence:` TST-20260215-010
- `Regression risk:` Low
- `Linked change:` CHG-20260215-010

## BUG-20260215-006
- `Title:` OpenClaw and orchestration paths were brittle against variable agent outputs and missing renderable cuts
- `Date reported:` 2026-02-15
- `Reported by:` Codex reliability review
- `Owner:` Backend Developer
- `Severity:` S2
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Strategy generation could fail on schema drift (`dict` vs model), color filter extraction used wrong key, and orchestrator could proceed with empty valid cuts/output parts.
- `Expected behavior:` Strategy generation should degrade gracefully and renderer should fail fast on invalid/no-output batches.
- `Root cause:` Strict attribute assumptions in `openclaw_service` and missing guard checks in `rendering_orchestrator`; n8n events lacked idempotency metadata and QA payload propagation.
- `Fix summary:` Normalized OpenClaw outputs + parallel specialist execution with fallback handling, enriched/signed n8n payload headers/body, persisted empty QA payloads in status updates, and added no-valid-cut/no-output safeguards.
- `Files changed:`
  - `backend/app/services/openclaw_service.py`
  - `backend/app/services/n8n_service.py`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/services/rendering_orchestrator.py`
  - `backend/tests/test_openclaw_service.py`
  - `backend/tests/test_n8n_service.py`
- `Validation evidence:` TST-20260215-009
- `Regression risk:` Low
- `Linked change:` CHG-20260215-009

## BUG-20260215-005
- `Title:` Frontend did not expose new post-depth controls, causing backend post settings to remain defaulted
- `Date reported:` 2026-02-15
- `Reported by:` Codex implementation review
- `Owner:` Backend Developer + Frontend Developer
- `Severity:` S3
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Users could not set transition/speed/subtitle/color/skin options from upload/edit UI, so jobs used defaults despite backend support.
- `Expected behavior:` Upload and re-edit UI should collect post-depth fields and include them in API payloads.
- `Root cause:` Backend schema/router support was added before corresponding frontend controls and payload wiring.
- `Fix summary:` Added post-depth controls in upload/edit pages and backend integration tests that assert `post_settings` persistence.
- `Files changed:`
  - `frontend/app/dashboard/upload/page.tsx`
  - `frontend/app/jobs/[id]/JobPageClient.tsx`
  - `backend/tests/test_jobs.py`
- `Validation evidence:` TST-20260215-008
- `Regression risk:` Low
- `Linked change:` CHG-20260215-008

## BUG-20260215-004
- `Title:` AI pipeline could return source-identical outputs when cut plans were empty or pass-through
- `Date reported:` 2026-02-15
- `Reported by:` User feedback + Codex analysis
- `Owner:` Backend Developer
- `Severity:` S2
- `Status:` Resolved
- `Environment:` Local
- `Symptoms:` Final videos looked identical to input because fallback/full-span cuts preserved nearly all source content.
- `Expected behavior:` AI paths should produce visible edits by default, even when model output is weak or malformed.
- `Root cause:` Cut lists were accepted without guardrails for pass-through ratio or empty responses.
- `Fix summary:` Added `ensure_editing_cuts(...)` policy to normalize and replace pass-through plans with pacing-aware highlight cuts in Standard and Pro compiler paths.
- `Files changed:`
  - `backend/app/services/workflow_engine.py`
  - `backend/app/graph/nodes/compiler.py`
  - `backend/tests/test_editing_cuts.py`
- `Validation evidence:` TST-20260215-004
- `Regression risk:` Low
- `Linked change:` CHG-20260215-004

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
