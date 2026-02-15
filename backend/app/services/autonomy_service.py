from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError

from ..agents.maintenance_agent import maintenance_agent
from ..agents.routing_policy import provider_router
from ..config import settings
from ..db import SessionLocal
from ..models import Job
from .cleanup_service import cleanup_service
from .integration_health import get_integration_health
from .introspection import introspection_service
from .llm_health import get_llm_health_summary

logger = structlog.get_logger()


class AutonomyService:
    """Background idle loop for safe self-healing and bounded self-improvement."""

    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._lock = asyncio.Lock()
        self._last_heal: datetime | None = None
        self._last_improve: datetime | None = None
        self._last_result: dict[str, Any] = {"status": "never_run"}
        self._metrics: dict[str, int] = {
            "run_count": 0,
            "heal_count": 0,
            "improve_count": 0,
            "skip_high_load_count": 0,
        }
        self._profile_mode = "conservative"
        self._profiles: dict[str, dict[str, float]] = {
            "conservative": {
                "poll_seconds": max(5, int(settings.autonomy_poll_seconds)),
                "heal_interval_seconds": max(60, int(settings.autonomy_idle_heal_interval_seconds)),
                "improve_interval_seconds": max(300, int(settings.autonomy_idle_improve_interval_seconds)),
                "cleanup_max_age_hours": 12,
                "provider_failure_threshold": 8,
                "provider_success_rate_threshold": 0.35,
                "provider_circuit_seconds": 300,
                "max_cpu_percent": 85.0,
                "max_memory_percent": 90.0,
            },
            "aggressive": {
                "poll_seconds": 10,
                "heal_interval_seconds": 90,
                "improve_interval_seconds": 600,
                "cleanup_max_age_hours": 6,
                "provider_failure_threshold": 5,
                "provider_success_rate_threshold": 0.50,
                "provider_circuit_seconds": 180,
                "max_cpu_percent": 92.0,
                "max_memory_percent": 94.0,
            },
        }
        configured_mode = (settings.autonomy_profile_mode or "conservative").strip().lower()
        if configured_mode in self._profiles:
            self._profile_mode = configured_mode
        self._profile = dict(self._profiles[self._profile_mode])

    async def start(self) -> None:
        if not settings.autonomy_enabled:
            logger.info("autonomy_disabled")
            return
        if self._task and not self._task.done():
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._loop(), name="autonomy-idle-loop")
        logger.info("autonomy_started")

    async def stop(self) -> None:
        self._stop.set()
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("autonomy_stopped")

    def get_status(self) -> dict[str, Any]:
        return {
            "enabled": settings.autonomy_enabled,
            "running": bool(self._task and not self._task.done()),
            "profile_mode": self._profile_mode,
            "profile": self._profile,
            "available_profiles": sorted(self._profiles.keys()),
            "metrics": self._metrics,
            "last_heal_at": self._last_heal.isoformat() if self._last_heal else None,
            "last_improve_at": self._last_improve.isoformat() if self._last_improve else None,
            "last_result": self._last_result,
        }

    def set_profile(self, mode: str) -> dict[str, Any]:
        normalized = (mode or "").strip().lower()
        if normalized not in self._profiles:
            raise ValueError(f"Unsupported autonomy profile: {mode}")
        self._profile_mode = normalized
        self._profile = dict(self._profiles[normalized])
        logger.info("autonomy_profile_updated", mode=self._profile_mode, profile=self._profile)
        return self.get_status()

    async def run_once(self, force_improve: bool = False, force_heal: bool = False) -> dict[str, Any]:
        async with self._lock:
            self._metrics["run_count"] += 1
            recovered = await self._recover_stuck_jobs()
            idle = await self._is_system_idle()
            now = datetime.utcnow()

            load = await self._get_system_load()
            high_load = load["cpu_percent"] >= self._profile["max_cpu_percent"] or load["memory_percent"] >= self._profile["max_memory_percent"]
            if high_load and not (force_heal or force_improve):
                self._metrics["skip_high_load_count"] += 1

            should_heal = force_heal or (
                idle and not high_load and self._due(now, self._last_heal, int(self._profile["heal_interval_seconds"]))
            )
            should_improve = force_improve or (
                idle and not high_load and self._due(now, self._last_improve, int(self._profile["improve_interval_seconds"]))
            )

            result: dict[str, Any] = {
                "idle": idle,
                "high_load": high_load,
                "load": load,
                "recovered_stuck_jobs": recovered,
                "heal_ran": False,
                "improve_ran": False,
                "actions": [],
            }

            if should_heal:
                heal_result = await self._run_heal_cycle()
                result["heal_ran"] = True
                result["heal"] = heal_result
                self._last_heal = now
                self._metrics["heal_count"] += 1

            if should_improve:
                improve_result = await self._run_improve_cycle()
                result["improve_ran"] = True
                result["improve"] = improve_result
                self._last_improve = now
                self._metrics["improve_count"] += 1

            self._last_result = result
            return result

    async def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                await self.run_once(force_improve=False, force_heal=False)
            except Exception as exc:
                logger.error("autonomy_loop_failed", error=str(exc))
            await asyncio.sleep(max(5, int(self._profile["poll_seconds"])))

    @staticmethod
    def _due(now: datetime, last_run: datetime | None, interval_seconds: int) -> bool:
        if last_run is None:
            return True
        return now - last_run >= timedelta(seconds=max(1, int(interval_seconds)))

    async def _is_system_idle(self) -> bool:
        try:
            async with SessionLocal() as session:
                active = await session.scalar(
                    select(func.count()).select_from(Job).where(Job.status.in_(["queued", "processing"]))
                )
            return int(active or 0) == 0
        except SQLAlchemyError as exc:
            logger.warning("autonomy_idle_check_failed", error=str(exc))
            return False

    async def _recover_stuck_jobs(self) -> int:
        cutoff = datetime.utcnow() - timedelta(minutes=max(10, int(settings.autonomy_stuck_job_minutes)))
        try:
            async with SessionLocal() as session:
                result = await session.execute(
                    update(Job)
                    .where(Job.status == "processing", Job.updated_at < cutoff)
                    .values(
                        status="failed",
                        progress_message="Auto-healed: processing timeout exceeded. Retry recommended.",
                    )
                )
                await session.commit()
                recovered = int(result.rowcount or 0)
        except SQLAlchemyError as exc:
            logger.warning("autonomy_stuck_recovery_failed", error=str(exc))
            return 0

        if recovered > 0:
            logger.warning("autonomy_recovered_stuck_jobs", recovered=recovered)
        return recovered

    async def _run_heal_cycle(self) -> dict[str, Any]:
        introspection = await asyncio.to_thread(introspection_service.self_heal)
        integrations = await asyncio.to_thread(get_integration_health, False)
        llm_health = get_llm_health_summary()
        provider_actions = self._heal_provider_routing(llm_health)
        freed_bytes = await cleanup_service.run_cleanup(max_age_hours=int(self._profile["cleanup_max_age_hours"]))

        payload = {
            "introspection": introspection,
            "integrations": integrations,
            "llm": llm_health,
            "provider_actions": provider_actions,
            "cleanup_freed_bytes": freed_bytes,
        }
        logger.info("autonomy_heal_cycle_complete", provider_actions=len(provider_actions), cleanup_freed_bytes=freed_bytes)
        return payload

    async def _run_improve_cycle(self) -> dict[str, Any]:
        audit = await maintenance_agent.run({"task": "audit"})
        issue_count = len((audit or {}).get("issues", []))
        integrity_score = (audit or {}).get("integrity_score")
        logger.info("autonomy_improve_cycle_complete", issue_count=issue_count, integrity_score=integrity_score)
        return {
            "integrity_score": integrity_score,
            "issue_count": issue_count,
            "issues": (audit or {}).get("issues", [])[:20],
        }

    def _heal_provider_routing(self, llm_health: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        for provider_name, health in llm_health.items():
            if not health.get("configured"):
                continue
            success_rate = float(health.get("success_rate", 1.0))
            failure_count = int(health.get("failure_count", 0))
            is_healthy = bool(health.get("is_healthy", True))
            provider_state = provider_router.health[provider_name]

            # Conservative circuit opening to avoid repeated failures while idle.
            if (
                failure_count >= int(self._profile["provider_failure_threshold"])
                and success_rate < float(self._profile["provider_success_rate_threshold"])
                and is_healthy
            ):
                provider_state.open_circuit_for(float(self._profile["provider_circuit_seconds"]))
                actions.append(
                    {
                        "provider": provider_name,
                        "action": "open_circuit",
                        "seconds": int(self._profile["provider_circuit_seconds"]),
                        "reason": "high_failure_low_success_rate",
                    }
                )
        return actions

    async def _get_system_load(self) -> dict[str, float]:
        metrics = await asyncio.to_thread(introspection_service.get_live_metrics)
        system = (metrics or {}).get("system") or {}
        return {
            "cpu_percent": float(system.get("cpu_percent", 0.0) or 0.0),
            "memory_percent": float(system.get("memory_percent", 0.0) or 0.0),
        }


autonomy_service = AutonomyService()
