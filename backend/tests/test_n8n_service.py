import pytest
from types import SimpleNamespace

from app.config import settings
from app.services.n8n_service import N8NService
from app.services import workflow_engine


@pytest.mark.asyncio
async def test_n8n_service_retries_and_returns_false_when_down(monkeypatch):
    service = N8NService()

    monkeypatch.setattr(settings, "n8n_base_url", "http://127.0.0.1:5678", raising=False)
    monkeypatch.setattr(settings, "n8n_job_status_path", "/webhook/proedit/job-status", raising=False)
    monkeypatch.setattr(settings, "n8n_webhook_secret", "test-secret", raising=False)
    monkeypatch.setattr(settings, "n8n_retry_attempts", 2, raising=False)
    monkeypatch.setattr(settings, "n8n_retry_backoff_seconds", 0.0, raising=False)
    monkeypatch.setattr(settings, "n8n_timeout_seconds", 0.2, raising=False)

    attempts = {"count": 0}

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, content, headers):
            attempts["count"] += 1
            raise RuntimeError("n8n unavailable")

    monkeypatch.setattr("app.services.n8n_service.httpx.AsyncClient", FakeAsyncClient)

    job = SimpleNamespace(
        id=11,
        user_id=3,
        status="failed",
        progress_message="failed",
        output_path=None,
        thumbnail_path=None,
        tier="pro",
        platform="youtube",
    )

    ok = await service.send_job_status_event(job)
    assert ok is False
    assert attempts["count"] == 3  # first try + 2 retries


@pytest.mark.asyncio
async def test_n8n_service_adds_signature_header(monkeypatch):
    service = N8NService()

    monkeypatch.setattr(settings, "n8n_base_url", "http://127.0.0.1:5678", raising=False)
    monkeypatch.setattr(settings, "n8n_job_status_path", "/webhook/proedit/job-status", raising=False)
    monkeypatch.setattr(settings, "n8n_webhook_secret", "test-secret", raising=False)
    monkeypatch.setattr(settings, "n8n_retry_attempts", 0, raising=False)
    monkeypatch.setattr(settings, "n8n_timeout_seconds", 0.2, raising=False)

    captured = {}

    class FakeResponse:
        status_code = 200

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, content, headers):
            captured["url"] = url
            captured["content"] = content
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr("app.services.n8n_service.httpx.AsyncClient", FakeAsyncClient)

    job = SimpleNamespace(
        id=12,
        user_id=9,
        status="complete",
        progress_message="done",
        output_path="storage/outputs/job-12.mp4",
        thumbnail_path=None,
        tier="pro",
        platform="youtube",
    )

    ok = await service.send_job_status_event(job)
    assert ok is True
    assert captured["url"] == "http://127.0.0.1:5678/webhook/proedit/job-status"
    assert "X-ProEdit-Signature" in captured["headers"]
    assert captured["headers"]["X-ProEdit-Signature"].startswith("sha256=")


@pytest.mark.asyncio
async def test_update_status_does_not_fail_when_n8n_notification_errors(monkeypatch):
    class FakeJob:
        def __init__(self):
            self.id = 7
            self.user_id = 5
            self.cancel_requested = False
            self.status = "processing"
            self.progress_message = ""
            self.output_path = None
            self.thumbnail_path = None
            self.media_intelligence = None
            self.qc_result = None
            self.director_plan = None
            self.brand_safety_result = None
            self.ab_test_result = None
            self.performance_metrics = None

    fake_job = FakeJob()

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, model, job_id):
            return fake_job

        async def commit(self):
            return None

    async def failing_notify(job):
        raise RuntimeError("n8n down")

    monkeypatch.setattr(workflow_engine, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(workflow_engine.n8n_service, "send_job_status_event", failing_notify)

    await workflow_engine.update_status(7, "failed", "Processing failed")
    assert fake_job.status == "failed"
    assert fake_job.progress_message == "Processing failed"
