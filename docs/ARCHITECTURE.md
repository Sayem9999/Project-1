# ProEdit Studio Architecture

## Overview
ProEdit is a distributed video editing platform that leverages AI agents and serverless GPUs to provide professional-grade video editing at scale.

## Core Components

### 1. API Server (FastAPI)
- Handles user authentication, job submissions, and status tracking.
- Implements a resilient `admin_cache` for zero-wait dashboard statistics.
- Hardened Celery diagnostics to prevent startup stalls if workers are unavailable.

### 2. Database (SQLite/PostgreSQL)
- Uses `aiosqlite` for asynchronous local development.
- Stores user credits, job history, and performance metrics.
- WAL mode enabled for high concurrency.

### 3. Background Worker (Celery + Redis)
- Dispatches intensive video processing tasks.
- Dedicated `video_local` queue for proximity-based processing.
- Handles multi-phase workflows via LangGraph.

### 4. Storage (S3/R2)
- Cloudflare R2 for durable asset storage.
- Local `storage/temp` for intermediate processing files.
- `CleanupService` for maintaining disk hygiene.

## Key Services
- **Introspection Service**: Scans the codebase to build a dependency graph for AI assistants.
- **Workflow Engine**: Orchestrates the "Hollywood Pipeline" (Director, Cutter, Audio, Visuals).
- **Metric Service**: Tracks duration and costs for every job phase.
  - Reliability hotspot analysis is computed from first-party workflow metrics (including stage timeout totals/counts); no external search API is required for timeout monitoring.
- **OpenClaw Service**: Generates technical edit strategy for external orchestration with resilient agent-output normalization and specialist fallback handling.
- **n8n Service**: Sends terminal job events with signed payloads, retries/backoff, and event-level idempotency headers.
- **Rendering Orchestrator**: Parallel scene renderer with speed/keyframe/transition support and strict guards for invalid/no-output cut batches.

## Orchestration Contract
- **Ingress**:
  - `/api/orchestration/context/{job_id}` provides source path + media intelligence.
  - `/api/orchestration/strategy/{job_id}` returns OpenClaw strategy (`cuts`, `vf_filters`, `af_filters`, metadata).
  - `/api/orchestration/callback/{job_id}` accepts finalized strategy and triggers `render_orchestrated_job`.
- **Callback security**:
  - HMAC verification on raw request body with `X-ProEdit-Timestamp` and `X-ProEdit-Signature`.
  - Replay protection via required `X-ProEdit-Event-Id` deduped in `processed_webhooks`.
  - Timestamp window enforcement (`ORCHESTRATION_WEBHOOK_TOLERANCE_SECONDS`).
- **Egress**:
  - Terminal status notifications (`complete`/`failed`) are delivered to n8n via `N8NService`.
  - Headers: `X-ProEdit-Timestamp`, `X-ProEdit-Signature`, `X-ProEdit-Event-Id`, `X-ProEdit-Attempt`.
  - Payload includes job metadata plus `post_settings` and QA blocks (`audio_qa`, `color_qa`, `subtitle_qa`) when available.
- **Safety rules**:
  - Workflow status updates persist QA payloads even when empty dictionaries are supplied.
  - Orchestrator rejects batches with no valid cuts or no rendered scene outputs before concat.

## Reliability Features
- **Transient Error Retry**: Robust retry mechanism (max 2 attempts) for "transient" errors (timeouts, connection drops) in AI provider calls.
- **Admin Cache Optimization**: Concurrent execution of stats gathering (DB, Storage, Health) ensures dashboard latency <1s.
- **Health Probing**: Real-time monitoring of Gemini, Redis, and Modal integrations.
- **Timeout Reliability Summary**: Admin endpoint `/api/maintenance/reliability/timeout-summary` exposes recent timeout rate, per-stage hotspots, and threshold alerts.
- **Auto-Cleanup**: Automated purging of stale local temp files.
- **Idempotency**: "Cleanup Stuck Jobs" on startup ensures system state consistency.
- **Idle Autonomy Loop**: When no queued/processing jobs exist, backend runs guarded self-heal and self-improve cycles:
  - self-heal: introspection graph heal, integration probes, LLM routing circuit protection, cleanup sweep
  - self-improve: maintenance audit pass with integrity score and issue surfacing
  - admin APIs: `/api/maintenance/autonomy/status` and `/api/maintenance/autonomy/run`
  - profile tuning: `conservative` and `aggressive` runtime profiles with load guards + counters
  - profile API: `/api/maintenance/autonomy/profile?mode=...`
  - frontend control surface: Admin `System` tab autonomy panel
  - auditability: autonomy mode changes and forced runs are persisted in `admin_action_logs` and exposed at `/api/admin/audit/actions`
