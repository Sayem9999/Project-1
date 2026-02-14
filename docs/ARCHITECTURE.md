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

## Reliability Features
- **Health Probing**: Real-time monitoring of Gemini, Redis, and Modal integrations.
- **Auto-Cleanup**: Automated purging of stale local temp files.
- **Idempotency**: "Cleanup Stuck Jobs" on startup ensures system state consistency.
