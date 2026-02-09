"""
Metrics Collector - Track objective metrics per video output for benchmarking.
Enables auto-tuning loop by feeding metrics back into policy.
"""
import structlog
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json

logger = structlog.get_logger()


@dataclass
class OutputMetrics:
    """Objective metrics for a video output."""
    job_id: int
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Audio metrics
    loudness_lufs: Optional[float] = None
    true_peak_dbfs: Optional[float] = None
    loudness_compliant: bool = False  # Meets target LUFS
    
    # Subtitle metrics
    subtitle_overlap_pct: Optional[float] = None  # % of subtitles overlapping
    subtitle_readability: Optional[float] = None  # Chars per second
    
    # Visual metrics
    black_frame_pct: Optional[float] = None
    avg_shot_length_sec: Optional[float] = None
    scene_count: Optional[int] = None
    
    # Performance metrics
    render_time_sec: Optional[float] = None
    agent_time_sec: Optional[float] = None
    total_processing_time_sec: Optional[float] = None
    
    # Quality scores
    qc_score: Optional[int] = None  # 1-10 from QC agent
    qc_approved: bool = False
    user_rating: Optional[int] = None  # 1-5 user satisfaction
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkThresholds:
    """Quality thresholds for automated benchmarking."""
    # Audio
    target_lufs: float = -14.0
    lufs_tolerance: float = 1.0
    max_true_peak: float = -1.0
    
    # Subtitles
    max_subtitle_overlap_pct: float = 5.0
    max_chars_per_second: float = 25.0
    
    # Visual
    max_black_frame_pct: float = 2.0
    min_shot_length: float = 0.5
    max_shot_length: float = 30.0
    
    # Performance
    max_render_time_multiplier: float = 2.0  # max 2x realtime
    
    # Quality
    min_qc_score: int = 6


class MetricsCollector:
    """
    Collect and store metrics for benchmarking and auto-tuning.
    """
    
    def __init__(self, storage_path: str = "storage/metrics"):
        self.storage_path = storage_path
        self.thresholds = BenchmarkThresholds()
        self._metrics_history: List[OutputMetrics] = []
    
    def record(self, metrics: OutputMetrics) -> None:
        """Record metrics for a job."""
        self._metrics_history.append(metrics)
        
        # Log summary
        logger.info(
            "metrics_recorded",
            job_id=metrics.job_id,
            qc_approved=metrics.qc_approved,
            loudness_compliant=metrics.loudness_compliant,
            render_time=metrics.render_time_sec
        )
        
        # Persist to file
        self._persist(metrics)
    
    def _persist(self, metrics: OutputMetrics) -> None:
        """Persist metrics to storage."""
        import os
        os.makedirs(self.storage_path, exist_ok=True)
        
        filename = f"{self.storage_path}/metrics_{metrics.job_id}.json"
        with open(filename, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)
    
    def evaluate_compliance(self, metrics: OutputMetrics) -> Dict[str, bool]:
        """Check if metrics meet quality thresholds."""
        t = self.thresholds
        
        compliance = {
            "loudness": True,
            "peak": True,
            "subtitles": True,
            "black_frames": True,
            "shot_length": True,
            "render_time": True,
            "qc_score": True,
        }
        
        # Check loudness
        if metrics.loudness_lufs is not None:
            deviation = abs(metrics.loudness_lufs - t.target_lufs)
            compliance["loudness"] = deviation <= t.lufs_tolerance
        
        # Check true peak
        if metrics.true_peak_dbfs is not None:
            compliance["peak"] = metrics.true_peak_dbfs <= t.max_true_peak
        
        # Check subtitles
        if metrics.subtitle_overlap_pct is not None:
            compliance["subtitles"] = metrics.subtitle_overlap_pct <= t.max_subtitle_overlap_pct
        
        if metrics.subtitle_readability is not None:
            compliance["subtitles"] = compliance["subtitles"] and \
                metrics.subtitle_readability <= t.max_chars_per_second
        
        # Check black frames
        if metrics.black_frame_pct is not None:
            compliance["black_frames"] = metrics.black_frame_pct <= t.max_black_frame_pct
        
        # Check shot length
        if metrics.avg_shot_length_sec is not None:
            compliance["shot_length"] = (
                metrics.avg_shot_length_sec >= t.min_shot_length and
                metrics.avg_shot_length_sec <= t.max_shot_length
            )
        
        # Check QC score
        if metrics.qc_score is not None:
            compliance["qc_score"] = metrics.qc_score >= t.min_qc_score
        
        return compliance
    
    def get_aggregate_stats(self, last_n: int = 100) -> Dict[str, Any]:
        """Get aggregate statistics for recent outputs."""
        recent = self._metrics_history[-last_n:]
        if not recent:
            return {}
        
        # Calculate averages
        qc_scores = [m.qc_score for m in recent if m.qc_score is not None]
        render_times = [m.render_time_sec for m in recent if m.render_time_sec is not None]
        user_ratings = [m.user_rating for m in recent if m.user_rating is not None]
        
        return {
            "total_outputs": len(recent),
            "qc_approval_rate": sum(1 for m in recent if m.qc_approved) / len(recent) * 100,
            "avg_qc_score": sum(qc_scores) / len(qc_scores) if qc_scores else None,
            "avg_render_time": sum(render_times) / len(render_times) if render_times else None,
            "avg_user_rating": sum(user_ratings) / len(user_ratings) if user_ratings else None,
            "loudness_compliance_rate": sum(1 for m in recent if m.loudness_compliant) / len(recent) * 100
        }
    
    def get_policy_recommendations(self) -> Dict[str, Any]:
        """
        Analyze metrics and recommend policy adjustments.
        This feeds into the auto-tuning loop.
        """
        stats = self.get_aggregate_stats()
        recommendations = []
        
        if not stats:
            return {"recommendations": [], "stats": {}}
        
        # Low QC approval rate
        if stats.get("qc_approval_rate", 100) < 80:
            recommendations.append({
                "issue": "low_qc_approval",
                "action": "increase_quality_tier",
                "reason": f"QC approval rate is {stats['qc_approval_rate']:.1f}%"
            })
        
        # Low user ratings
        avg_rating = stats.get("avg_user_rating")
        if avg_rating and avg_rating < 3.5:
            recommendations.append({
                "issue": "low_user_satisfaction",
                "action": "review_agent_prompts",
                "reason": f"Average user rating is {avg_rating:.1f}/5"
            })
        
        # Slow render times
        avg_render = stats.get("avg_render_time")
        if avg_render and avg_render > 120:
            recommendations.append({
                "issue": "slow_rendering",
                "action": "optimize_ffmpeg_presets",
                "reason": f"Average render time is {avg_render:.0f}s"
            })
        
        # Poor loudness compliance
        if stats.get("loudness_compliance_rate", 100) < 90:
            recommendations.append({
                "issue": "loudness_issues",
                "action": "review_audio_pipeline",
                "reason": f"Loudness compliance is {stats['loudness_compliance_rate']:.1f}%"
            })
        
        return {
            "recommendations": recommendations,
            "stats": stats
        }


# Global collector instance
metrics_collector = MetricsCollector()
