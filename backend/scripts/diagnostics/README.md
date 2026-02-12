# Diagnostics Scripts

This folder contains one-off troubleshooting scripts that were previously kept in `backend/`.

## Purpose

- Keep the backend root focused on runtime/app files.
- Isolate ad-hoc diagnostics from production code paths.

## Usage

Run from the backend directory so imports and `.env` resolution remain consistent:

```powershell
cd backend
.\.venv\Scripts\python.exe .\scripts\diagnostics\<script_name>.py
```

Examples:

- `test_celery_hang.py`: inspect Celery/Redis behavior during worker connectivity issues.
- `verify_admin_health.py`: sanity-check admin health endpoints and timing.
- `debug_pipeline.py`: trace pipeline dispatch and runtime state.

These scripts are diagnostic tools and should not be imported by application modules.
