import asyncio
import os

class ConcurrencyLimits:
    """
    Centralized semaphore management for resource-constrained environments.
    Separates light tasks (Metadata/Planning) from heavy tasks (Rendering/Analysis fallback).
    """
    def __init__(self):
        # Analysis semaphore: Used for backend-side decoding (scenes/loudness)
        # We keep this at 1 to prevent OOM during fallback decoding.
        self.analysis_semaphore = asyncio.Semaphore(1)
        
        # Rendering semaphore: The heaviest RAM/CPU task.
        # MUST be 1 on 512MB tier. 
        self.render_semaphore = asyncio.Semaphore(1)
        
        # Limit for total concurrent tasks in Python (Planning/API)
        # Increasing this slightly since analysis is now often offloaded.
        self.max_concurrent_jobs = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))

limits = ConcurrencyLimits()
