import time
import structlog
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = structlog.get_logger()

@dataclass
class PerformanceTracker:
    job_id: int
    start_time: float = field(default_factory=time.time)
    phases: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def start_phase(self, phase_name: str):
        self.metadata[f"{phase_name}_start"] = time.time()
        logger.info("phase_start", job_id=self.job_id, phase=phase_name)

    def end_phase(self, phase_name: str):
        start = self.metadata.get(f"{phase_name}_start")
        if start:
            duration = (time.time() - start) * 1000  # ms
            self.phases[phase_name] = round(duration, 2)
            logger.info("phase_end", job_id=self.job_id, phase=phase_name, duration_ms=duration)

    def get_metrics(self) -> Dict[str, Any]:
        total_duration = (time.time() - self.start_time) * 1000
        stage_timeout_counts = self.metadata.get("stage_timeout_counts", {})
        stage_timeout_total = int(self.metadata.get("stage_timeout_total", 0) or 0)
        return {
            "total_duration_ms": round(total_duration, 2),
            "phase_durations": self.phases,
            "timestamp": datetime.utcnow().isoformat(),
            "estimated_cost": self._calculate_cost(),
            "stage_timeout_total": stage_timeout_total,
            "stage_timeout_counts": stage_timeout_counts,
        }

    def _calculate_cost(self) -> Dict[str, float]:
        # Placeholder for actual cost calculation logic
        # Gemini 1.5 Flash: ~$0.075 / 1M tokens (input), $0.3 / 1M (output)
        # Modal: ~$0.0001 per GPU second
        return {
            "gemini_usd": 0.002, # Estimated base
            "modal_usd": 0.0,    # Updated if modal used
            "total_usd": 0.002
        }

class MetricsService:
    def __init__(self):
        self.active_trackers: Dict[int, PerformanceTracker] = {}

    def get_tracker(self, job_id: int) -> PerformanceTracker:
        if job_id not in self.active_trackers:
            self.active_trackers[job_id] = PerformanceTracker(job_id=job_id)
        return self.active_trackers[job_id]

    def finalize(self, job_id: int) -> Dict[str, Any]:
        tracker = self.active_trackers.pop(job_id, None)
        if tracker:
            return tracker.get_metrics()
        return {}

metrics_service = MetricsService()
