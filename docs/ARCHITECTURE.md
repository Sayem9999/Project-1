# ProEdit Studio Architecture

## Overview
ProEdit is an AI-driven video editing studio that uses a hierarchical agent pipeline ("Hollywood Pipeline") to transform raw uploads into platform-optimized content.

## Backend Core
- **FastAPI**: Main API layer for authentication, job management, and specialist insights.
- **SQLAlchemy (SQLite)**: Persists user credits, job status, and rich agent metadata.
- **LangGraph**: Orchestrates the specialist agent workflow.
- **Celery / Redis (Upstash)**: Handles background processing.

### Specialist Agents
The system features a set of specialized agents that contribute to a `GraphState`:
- **Director**: Strategy and planning.
- **Cutter**: Timeline and trim points.
- **Brand Safety**: Content moderation and policy compliance.
- **A/B Test**: Alternative hook and title generation.
- **Eval Optimizer**: Final quality control and scoring.

### Data Flow (Specialists)
1. **Intelligence Phase**: Media metadata is extracted.
2. **Specialist Phase**: Agents execute in parallel, generating results.
3. **Storage**: Specialist outputs (`brand_safety_result`, `ab_test_result`) are captured in the `Job` model's JSON columns.
4. **Delivery**: The `JobResponse` schema includes these results for frontend consumption.

## Frontend
- **Next.js 15 (App Router)**: Modern dashboard and project status pages.
- **Lucide-React**: Iconography.
- **Dynamic Data Bento**: The Job Status page uses modular cards (`BrandSafetyCard`, `ABTestVariants`, `QCScoreBoard`) to visualize agent decisions.

## Infrastructure
- **R2 Storage**: Cloudflare storage for source videos and rendered outputs.
- **Upstash Redis**: Progress publishing and task queuing.
