import asyncio
import structlog
from ...config import settings
from ...services.metrics_service import metrics_service

logger = structlog.get_logger(__name__)


def get_stage_timeout_seconds() -> float:
    configured = float(getattr(settings, "ai_stage_timeout_seconds", 120.0))
    return max(5.0, configured)


def record_stage_timeout(stage: str, timeout_seconds: float, job_id: int | None = None) -> None:
    if job_id is None:
        return
    tracker = metrics_service.get_tracker(job_id)
    counts = tracker.metadata.setdefault("stage_timeout_counts", {})
    counts[stage] = int(counts.get(stage, 0) or 0) + 1
    tracker.metadata["stage_timeout_total"] = int(tracker.metadata.get("stage_timeout_total", 0) or 0) + 1
    tracker.metadata["last_stage_timeout"] = {
        "stage": stage,
        "timeout_seconds": timeout_seconds,
    }


async def run_with_stage_timeout(awaitable, *, stage: str, job_id: int | None = None):
    timeout = get_stage_timeout_seconds()
    try:
        return await asyncio.wait_for(awaitable, timeout=timeout)
    except asyncio.TimeoutError as exc:
        logger.warning(
            "graph_stage_timeout",
            stage=stage,
            job_id=job_id,
            timeout_seconds=timeout,
        )
        record_stage_timeout(stage=stage, timeout_seconds=timeout, job_id=job_id)
        raise TimeoutError(f"{stage} timed out after {timeout:.1f}s") from exc
