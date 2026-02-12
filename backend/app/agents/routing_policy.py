"""
Routing Policy - Policy-driven provider selection with health tracking.
Implements: task-based routing, response caching, provider health, critic separation.
"""
import hashlib
import time
import structlog
from typing import Dict, Any, Optional, List, Literal
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta
from ..config import settings

logger = structlog.get_logger()

TaskType = Literal["creative", "analytical", "qc", "simple", "complex", "multimodal"]
QualityTier = Literal["premium", "standard", "fast"]


@dataclass
class RoutingPolicy:
    """Policy for selecting AI provider."""
    task_type: TaskType = "simple"
    latency_budget_ms: int = 30000  # 30 seconds default
    max_cost_usd: float = 0.10
    min_quality_tier: QualityTier = "standard"
    prefer_cached: bool = True
    allow_fallback: bool = True


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    name: str
    models: List[str]
    quality_tier: QualityTier
    avg_latency_ms: int
    cost_per_1k_tokens: float
    supports_json: bool = True
    is_available: bool = True


@dataclass
class ProviderHealth:
    """Health status for a provider."""
    success_count: int = 0
    failure_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    circuit_open: bool = False
    circuit_open_until: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 1.0
    
    @property
    def is_healthy(self) -> bool:
        if self.circuit_open:
            if self.circuit_open_until and datetime.utcnow() < self.circuit_open_until:
                return False
            # Reset circuit
            self.circuit_open = False
        return self.success_rate > 0.5 or self.failure_count < 3

    def open_circuit_for(self, seconds: float) -> None:
        self.circuit_open = True
        self.circuit_open_until = datetime.utcnow() + timedelta(seconds=max(5, int(seconds)))


def _provider_configured(name: str) -> bool:
    if name == "openai":
        return bool(settings.openai_api_key)
    if name == "gemini":
        return bool(settings.gemini_api_key)
    if name == "groq":
        return bool(settings.groq_api_key)
    return False


# Provider configurations
PROVIDERS: Dict[str, ProviderConfig] = {
    "groq": ProviderConfig(
        name="groq",
        models=["llama-3.3-70b-versatile"],
        quality_tier="fast",
        avg_latency_ms=500,
        cost_per_1k_tokens=0.0  # Free tier
    ),
    "gemini": ProviderConfig(
        name="gemini",
        models=[
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ],
        quality_tier="standard",
        avg_latency_ms=2000,
        cost_per_1k_tokens=0.0  # Free tier
    ),
    "openai": ProviderConfig(
        name="openai",
        models=["gpt-4o-mini", "gpt-4o"],
        quality_tier="premium",
        avg_latency_ms=3000,
        cost_per_1k_tokens=0.15
    ),
}

# Task-type to preferred quality tier mapping
TASK_QUALITY_MAP: Dict[TaskType, QualityTier] = {
    "creative": "premium",
    "analytical": "standard",
    "qc": "premium",  # QC needs high quality
    "simple": "fast",
    "complex": "premium",
    "multimodal": "premium",
}


class ProviderRouter:
    """
    Policy-driven provider selection with health tracking and caching.
    """
    
    def __init__(self):
        self.health: Dict[str, ProviderHealth] = defaultdict(ProviderHealth)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(hours=1)
    
    def select_provider(
        self, 
        policy: RoutingPolicy,
        exclude: Optional[List[str]] = None
    ) -> Optional[ProviderConfig]:
        """Select best provider based on policy and health."""
        exclude = exclude or []
        candidates = []
        
        # Determine required quality tier from task type
        required_tier = TASK_QUALITY_MAP.get(policy.task_type, policy.min_quality_tier)
        
        tier_priority = {"premium": 3, "standard": 2, "fast": 1}
        required_priority = tier_priority.get(required_tier, 1)
        
        for name, config in PROVIDERS.items():
            if name in exclude:
                continue
            
            if not config.is_available:
                continue

            if not _provider_configured(name):
                continue
            
            # Check health
            health = self.health[name]
            if not health.is_healthy:
                logger.debug("provider_unhealthy", provider=name, success_rate=health.success_rate)
                continue
            
            # Check quality tier
            provider_priority = tier_priority.get(config.quality_tier, 1)
            if provider_priority < required_priority and not policy.allow_fallback:
                continue
            
            # Check latency budget
            if config.avg_latency_ms > policy.latency_budget_ms:
                continue
            
            # Check cost
            estimated_cost = config.cost_per_1k_tokens * 2  # Assume ~2k tokens per request
            if estimated_cost > policy.max_cost_usd:
                continue
            
            candidates.append((name, config, provider_priority, health.success_rate))
        
        if not candidates:
            logger.warning("no_providers_available", policy=policy)
            return None

        preferred = (settings.llm_primary_provider or "").lower()
        if preferred:
            for name, config, _, _ in candidates:
                if name == preferred:
                    logger.info(
                        "provider_selected",
                        provider=config.name,
                        task_type=policy.task_type,
                        preferred=True
                    )
                    return config
        
        # Sort by: quality tier (desc), success rate (desc), latency (asc)
        candidates.sort(key=lambda x: (-x[2], -x[3], PROVIDERS[x[0]].avg_latency_ms))
        
        selected = candidates[0][1]
        logger.info("provider_selected", provider=selected.name, task_type=policy.task_type)
        return selected
    
    def record_success(self, provider_name: str, latency_ms: int):
        """Record successful request."""
        health = self.health[provider_name]
        health.success_count += 1
        health.last_success = datetime.utcnow()
        
        # Update average latency (simple moving average)
        config = PROVIDERS.get(provider_name)
        if config:
            config.avg_latency_ms = int(config.avg_latency_ms * 0.9 + latency_ms * 0.1)
    
    def record_failure(self, provider_name: str, error: str):
        """Record failed request and potentially open circuit."""
        health = self.health[provider_name]
        health.failure_count += 1
        health.last_failure = datetime.utcnow()
        
        logger.warning("provider_failure", provider=provider_name, error=error)
        
        # Open circuit if too many failures
        if health.failure_count >= 5 and health.success_rate < 0.5:
            health.circuit_open = True
            health.circuit_open_until = datetime.utcnow() + timedelta(minutes=5)
            logger.warning("circuit_opened", provider=provider_name, until=health.circuit_open_until)

    def handle_provider_error(self, provider_name: str, model: str, error: str) -> None:
        """Special-case provider errors (quota/model not found) to disable temporarily."""
        err = (error or "").lower()
        health = self.health[provider_name]
        config = PROVIDERS.get(provider_name)

        # Quota / rate limits -> open circuit with retry delay if present
        rate_limit_keywords = ["resource_exhausted", "quota", "rate limit", "429", "too many requests"]
        if any(kw in err for kw in rate_limit_keywords):
            # Default to 60s for rate limit if no specific time found
            retry_seconds = 60
            import re
            # Match formats like: "retry in 2.5s", "retry after 5 seconds", "try again in 10s"
            patterns = [
                r"retry in ([0-9]+(?:\.[0-9]+)?)s",
                r"retry after ([0-9]+(?:\.[0-9]+)?)s",
                r"retry in ([0-9]+(?:\.[0-9]+)?) seconds",
                r"try again in ([0-9]+(?:\.[0-9]+)?)s"
            ]
            for pattern in patterns:
                match = re.search(pattern, err)
                if match:
                    retry_seconds = float(match.group(1))
                    break
            
            # Additional check for raw JSON headers if passed in some error strings
            match = re.search(r"retrydelay['\"]?:\\s*'?([0-9]+)s", err)
            if match:
                retry_seconds = float(match.group(1))
                
            health.open_circuit_for(retry_seconds)
            logger.warning(
                "provider_quota_circuit_open",
                provider=provider_name,
                seconds=retry_seconds,
                error=err[:100]
            )
            return

        # Model not found -> drop model from list to avoid repeated failures
        if "not found" in err and config and model in config.models:
            config.models = [m for m in config.models if m != model]
            logger.warning("provider_model_disabled", provider=provider_name, model=model)
            if not config.models:
                health.open_circuit_for(600)
                logger.warning("provider_disabled_no_models", provider=provider_name)
    
    def get_cache_key(self, prompt: str, payload: Dict[str, Any]) -> str:
        """Compute cache key."""
        import json
        content = prompt + json.dumps(payload, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_cached(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if exists and not expired."""
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if datetime.utcnow() < entry["expires"]:
                logger.debug("cache_hit", key=cache_key[:16])
                return entry["response"]
            else:
                del self._cache[cache_key]
        return None
    
    def cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response with TTL."""
        self._cache[cache_key] = {
            "response": response,
            "expires": datetime.utcnow() + self._cache_ttl,
            "cached_at": datetime.utcnow()
        }
        
        # Cleanup old entries (simple approach)
        if len(self._cache) > 1000:
            now = datetime.utcnow()
            self._cache = {
                k: v for k, v in self._cache.items() 
                if v["expires"] > now
            }
    
    def get_qc_provider(self) -> ProviderConfig:
        """Get dedicated provider for QC/critic tasks (separate from main provider)."""
        # QC uses a different model to avoid bias
        qc_policy = RoutingPolicy(
            task_type="qc",
            min_quality_tier="premium",
            prefer_cached=False  # QC should not use cache
        )
        return self.select_provider(qc_policy) or PROVIDERS["gemini"]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for all providers."""
        return {
            name: {
                "success_rate": self.health[name].success_rate,
                "circuit_open": self.health[name].circuit_open,
                "is_healthy": self.health[name].is_healthy
            }
            for name in PROVIDERS
        }


# Global router instance
provider_router = ProviderRouter()


def get_routing_policy(task_type: TaskType = "simple") -> RoutingPolicy:
    """Convenience function to create a routing policy."""
    return RoutingPolicy(task_type=task_type)
