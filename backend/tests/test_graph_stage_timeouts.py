import asyncio

import pytest

from app.graph.nodes._timeouts import run_with_stage_timeout
from app.graph.nodes.platform import platform_node
from app.services.metrics_service import metrics_service


@pytest.mark.asyncio
async def test_run_with_stage_timeout_raises(monkeypatch):
    monkeypatch.setattr("app.graph.nodes._timeouts.get_stage_timeout_seconds", lambda: 0.01)

    async def slow():
        await asyncio.sleep(0.02)
        return "done"

    with pytest.raises(TimeoutError):
        await run_with_stage_timeout(slow(), stage="unit-test", job_id=1)


@pytest.mark.asyncio
async def test_platform_node_returns_fallback_on_timeout(monkeypatch):
    monkeypatch.setattr("app.graph.nodes._timeouts.get_stage_timeout_seconds", lambda: 0.01)

    async def slow_run(*args, **kwargs):
        await asyncio.sleep(0.02)

    monkeypatch.setattr("app.graph.nodes.platform.platform_agent.run", slow_run)

    state = {
        "job_id": 42,
        "user_request": {"platform": "youtube", "content_type": "short-form"},
        "director_plan": {},
    }

    result = await platform_node(state)
    assert "errors" in result
    assert "timed out" in result["errors"][0]
    assert result["platform_result"]["platform"] == "youtube"


@pytest.mark.asyncio
async def test_timeout_records_tracker_metrics(monkeypatch):
    job_id = 314
    metrics_service.active_trackers.pop(job_id, None)
    monkeypatch.setattr("app.graph.nodes._timeouts.get_stage_timeout_seconds", lambda: 0.01)

    async def slow():
        await asyncio.sleep(0.02)

    with pytest.raises(TimeoutError):
        await run_with_stage_timeout(slow(), stage="director", job_id=job_id)

    tracker = metrics_service.get_tracker(job_id)
    assert tracker.metadata["stage_timeout_total"] == 1
    assert tracker.metadata["stage_timeout_counts"]["director"] == 1

    finalized = metrics_service.finalize(job_id)
    assert finalized["stage_timeout_total"] == 1
    assert finalized["stage_timeout_counts"]["director"] == 1
