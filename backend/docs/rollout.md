# Production Rollout & Rollback Runbook

This document outlines the strategy for deploying the backend stabilization and hardening changes.

## Rollout Strategy

1.  **Preparation**:
    *   Ensure all environment variables for the target environment are set (especially `REDIS_URL`, `DATABASE_URL`, and `STRIPE_SECRET_KEY`).
    *   Verify that `pip-tools` is used to install dependencies to mirror the locked `requirements.txt`.

2.  **Deployment Steps**:
    *   **Pre-deploy**: Run `alembic upgrade head` to ensure migrations are applied.
    *   **Deploy**: Restart API and Worker processes.
    *   **Post-deploy**: Verify health endpoints (`/health`, `/ready`).

3.  **Verification**:
    *   Check logs for `startup_config` and `startup_migrations_complete`.
    *   Monitor Sentry for any new errors related to the new error taxonomy.

## Rollback Runbook

### Scenario 1: Migration Failure
If `alembic upgrade head` fails:
1.  Identify the failed migration.
2.  Restore the database from the last known backup.
3.  Revert the code to the previous stable version.

### Scenario 2: Dependency Conflicts
If the application fails to start due to `ImportError`:
1.  Check `requirements.txt` against the environment.
2.  If necessary, revert to `requirements.snapshot.txt` (the pre-upgrade snapshot).
3.  Run `pip install -r requirements.snapshot.txt`.

### Scenario 3: API Instability
If `/health` or `/ready` endpoints fail after deployment:
1.  Roll back to the previous stable code version immediately.
2.  Re-run migrations if any backward-incompatible changes were made (though none are expected in this phase).
