from __future__ import annotations

from ..config import settings
from ..agents.routing_policy import PROVIDERS, provider_router


def _provider_configured(name: str) -> bool:
    if name == "openai":
        return bool(settings.openai_api_key)
    if name == "gemini":
        return bool(settings.gemini_api_key)
    if name == "groq":
        return bool(settings.groq_api_key)
    return False


def get_llm_health_summary() -> dict[str, dict]:
    summary: dict[str, dict] = {}
    for name, config in PROVIDERS.items():
        health = provider_router.health[name]
        configured = _provider_configured(name)
        summary[name] = {
            "configured": configured,
            "available": configured,
            "models": config.models,
            "quality_tier": config.quality_tier,
            "avg_latency_ms": config.avg_latency_ms,
            "success_rate": health.success_rate,
            "success_count": health.success_count,
            "failure_count": health.failure_count,
            "last_success": health.last_success.isoformat() if health.last_success else None,
            "last_failure": health.last_failure.isoformat() if health.last_failure else None,
            "circuit_open": health.circuit_open,
            "circuit_open_until": health.circuit_open_until.isoformat() if health.circuit_open_until else None,
            "is_healthy": health.is_healthy and configured,
        }
    return summary
