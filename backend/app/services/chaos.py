import random
import asyncio
import structlog
from typing import Dict, Any, List
from ..config import settings
from ..agents.routing_policy import provider_router

logger = structlog.get_logger()

class ChaosMonkey:
    """
    Chaos Engineering utility for ProEdit.
    Simulates random failures to test system resilience and self-healing.
    """
    
    def __init__(self):
        self.is_active = False
        self.active_sabotages = []

    async def start_chaos_session(self, duration_sec: int = 60):
        """Start a period of random system failures."""
        logger.warning("chaos_monkey_unleashed", duration=duration_sec)
        self.is_active = True
        
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < duration_sec:
            if not self.is_active: break
            
            # Randomly trigger a sabotage
            sabotage_type = random.choice(["provider_latency", "provider_failure", "memory_spike"])
            await self._sabotage(sabotage_type)
            
            await asyncio.sleep(random.randint(5, 15))
            
        self.is_active = False
        logger.info("chaos_monkey_caged")

    async def _sabotage(self, sabotage_type: str):
        logger.warning("chaos_sabotage_triggered", type=sabotage_type)
        
        if sabotage_type == "provider_latency":
            # Inject fake latency into a random provider
            provider_name = random.choice(list(provider_router.health.keys()) or ["gemini"])
            provider_router.record_success(provider_name, 5000) # Inject 5s latency
            
        elif sabotage_type == "provider_failure":
            # Trigger a fake failure
            provider_name = random.choice(list(provider_router.health.keys()) or ["gemini"])
            provider_router.record_failure(provider_name, "Simulated ChaosMonkey Failure")

        elif sabotage_type == "memory_spike":
            # (Simulated) We just log it for the MaintenanceAgent to 'see' and 'fix'
            logger.error("system_resource_alert", resource="memory", usage="95%", threshold="90%")

# Global instance
chaos_monkey = ChaosMonkey()
