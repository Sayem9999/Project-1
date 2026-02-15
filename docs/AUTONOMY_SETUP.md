# Autonomy & Multi-Agent Architecture Setup

## Overview
This document describes the enabled Autonomy features for the ProEdit system, including the Multi-Agent architecture, Routing Policy, and Self-Healing capabilities.

## Architecture
The system uses a multi-agent approach orchestrated by the `AutonomyService` and `MaintenanceRouter`.

### Agents
1.  **Architect Agent** (`backend/app/agents/architect_agent.py`)
    *   **Role**: High-level system understanding, answering queries about the codebase graph.
    *   **Tools**: `introspection_service` (AST-based graph of nodes/edges).
    *   **Trigger**: POST `/api/maintenance/architect`

2.  **Maintenance Agent** (`backend/app/agents/maintenance_agent.py`)
    *   **Role**: Execution of code changes, self-healing, and feature population.
    *   **Tools**: File editing, semantic search (vector store).
    *   **Trigger**: POST `/api/maintenance/heal`, POST `/api/maintenance/populate`, or background loop.

### Routing Policy
*   **File**: `backend/app/agents/routing_policy.py`
*   **Purpose**: Dynamically selects the best LLM provider based on task type.
*   **Configuration**:
    *   **Primary**: OpenAI (GPT-4o) for complex/creative tasks.
    *   **Fallback**: Gemini (Flash) for speed/redundancy or if OpenAI is unreachable.
    *   **Cost Limit**: Increased to $1.00/request to allow premium model usage.

## Configuration Changes
*   **Environment**: Updated `.env` with `OPENAI_API_KEY`.
*   **Policy**: Updated `routing_policy.py` `max_cost_usd` to $1.00.

## Verification
*   **Script**: `backend/scripts/test_autonomy_llm.py` verifies the Maintenance Agent can generate code (scaffold).
*   **Connectivity**: `backend/scripts/check_openai_direct.py` checks direct OpenAI reachability.
*   **Logs**: Monitor terminal for `autonomy_step` and `provider_selected` events.

## Related Documentation
*   `docs/MULTI_AGENT_WORKFLOW.md`: Workflow roles and handoffs.
*   `docs/tracking/CHANGE_LOG.md`: Change history (see CHG-20260215-024).
