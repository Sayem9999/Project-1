# Backend Readiness

Use this checklist before running API/worker for real jobs.

## 1. Environment
- Copy `backend/.env.example` to `backend/.env`.
- Set at least one LLM key:
  - `GEMINI_API_KEY` or `GROQ_API_KEY` or `OPENAI_API_KEY`
- Keep `DATABASE_URL` on local SQLite for local runs unless PostgreSQL is intentional.
- If using n8n outbound notifications:
  - set `N8N_BASE_URL`
  - set `N8N_WEBHOOK_SECRET`

## 2. Preflight
- Run:
```bash
cd backend
make ready
```

This checks:
- ffmpeg availability (bundled or PATH)
- database connectivity
- redis connectivity (if configured)
- LLM key presence
- n8n config consistency

## 3. Start
- API:
```bash
cd backend
python -m uvicorn app.main:app --reload
```
- Worker (if Redis/Celery configured):
```bash
cd backend
python -m celery -A app.celery_app worker --loglevel=info -Q ${CELERY_VIDEO_QUEUE:-video}
```
