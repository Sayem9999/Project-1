"""
Hybrid Memory Service - Orchestrates Redis short-term and pgvector long-term memory.
Provides unified interface for agent context retrieval.
"""
import hashlib
import structlog
from typing import Optional, Dict, Any, List
from .redis_store import RedisMemoryStore, redis_store
from .vector_store import VectorMemoryStore, StyleProfile, Recipe, vector_store

logger = structlog.get_logger()


class HybridMemoryService:
    """
    Unified memory service that combines:
    - Redis: Short-term session state, recent context, response cache
    - pgvector: Long-term user profiles, successful recipes, semantic search
    """
    
    def __init__(
        self, 
        redis: RedisMemoryStore = None,
        vector: VectorMemoryStore = None
    ):
        self.redis = redis or redis_store
        self.vector = vector or vector_store
    
    async def get_agent_context(self, user_id: int, job_id: Optional[int] = None) -> str:
        """
        Build comprehensive context for agent prompts.
        Combines short-term and long-term memory.
        """
        context_parts = []
        
        # 1. Get user style profile from long-term memory
        profile = await self.vector.get_style_profile(user_id)
        if profile:
            context_parts.append(self._format_style_profile(profile))
        
        # 2. Get recent feedback from short-term memory
        recent_feedback = await self.redis.get_recent_context(user_id, "feedback", count=3)
        if recent_feedback:
            context_parts.append("**Recent Feedback:**\n" + "\n".join([f"- {f}" for f in recent_feedback]))
        
        # 3. Get user's top recipes
        recipes = await self.vector.get_user_recipes(user_id, limit=3)
        if recipes:
            context_parts.append(self._format_recipes(recipes))
        
        if not context_parts:
            return ""
        
        return "\n\n**MEMORY CONTEXT (User Preferences):**\n" + "\n\n".join(context_parts)
    
    def _format_style_profile(self, profile: StyleProfile) -> str:
        """Format style profile for prompt injection."""
        parts = [
            "**User Style Profile:**",
            f"- Pacing: {profile.pacing_preference}",
            f"- Color preference: {profile.color_preference}",
            f"- Audio focus: {profile.audio_preference}",
        ]
        if profile.favorite_transitions:
            parts.append(f"- Favorite transitions: {', '.join(profile.favorite_transitions)}")
        if profile.avoid_patterns:
            parts.append(f"- Avoid: {', '.join(profile.avoid_patterns)}")
        return "\n".join(parts)
    
    def _format_recipes(self, recipes: List[Recipe]) -> str:
        """Format recipes for prompt injection."""
        lines = ["**Successful Patterns:**"]
        for r in recipes:
            lines.append(f"- {r.name}: {r.description} (used {r.success_count} times)")
        return "\n".join(lines)
    
    async def record_feedback(self, user_id: int, feedback: str) -> None:
        """Record user feedback in short-term memory."""
        await self.redis.add_recent_context(user_id, "feedback", feedback)
        
        # Extract preferences if feedback contains persistent patterns
        if any(kw in feedback.lower() for kw in ["always", "never", "prefer", "hate"]):
            await self._update_style_from_feedback(user_id, feedback)
    
    async def _update_style_from_feedback(self, user_id: int, feedback: str) -> None:
        """Extract and update style preferences from feedback."""
        # Get or create profile
        profile = await self.vector.get_style_profile(user_id)
        if not profile:
            profile = StyleProfile(user_id=user_id)
        
        feedback_lower = feedback.lower()
        
        # Simple rule-based extraction (in production, use LLM)
        if "fast" in feedback_lower and "pacing" in feedback_lower:
            profile.pacing_preference = "fast"
        elif "slow" in feedback_lower and "pacing" in feedback_lower:
            profile.pacing_preference = "slow"
        
        if "warm" in feedback_lower and ("color" in feedback_lower or "tone" in feedback_lower):
            profile.color_preference = "warm"
        elif "cool" in feedback_lower and ("color" in feedback_lower or "tone" in feedback_lower):
            profile.color_preference = "cool"
        
        await self.vector.update_style_profile(profile)
        logger.info("style_updated_from_feedback", user_id=user_id)
    
    async def save_successful_pattern(
        self, 
        user_id: int,
        name: str,
        description: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """Save a successful editing pattern as a reusable recipe."""
        recipe_id = hashlib.sha256(f"{user_id}:{name}".encode()).hexdigest()[:16]
        
        recipe = Recipe(
            id=recipe_id,
            user_id=user_id,
            name=name,
            description=description,
            parameters=parameters
        )
        
        return await self.vector.save_recipe(recipe)
    
    async def check_cache(self, prompt: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if response is cached."""
        cache_key = self._compute_cache_key(prompt, payload)
        return await self.redis.get_cached_response(cache_key)
    
    async def cache_response(
        self, 
        prompt: str, 
        payload: Dict[str, Any], 
        response: Dict[str, Any]
    ) -> bool:
        """Cache agent response."""
        cache_key = self._compute_cache_key(prompt, payload)
        return await self.redis.cache_response(cache_key, response)
    
    def _compute_cache_key(self, prompt: str, payload: Dict[str, Any]) -> str:
        """Compute cache key from prompt and payload."""
        import json
        content = prompt + json.dumps(payload, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def close(self):
        """Close all connections."""
        await self.redis.close()
        await self.vector.close()


# Global hybrid memory instance
hybrid_memory = HybridMemoryService()
