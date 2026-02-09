"""
Vector Memory Store - Long-term memory using pgvector for semantic search.
Stores user style profiles, successful patterns (recipes), and preferences.
"""
import json
import hashlib
import structlog
from typing import Optional, Any, Dict, List
from datetime import datetime
from dataclasses import dataclass, asdict

logger = structlog.get_logger()

# pgvector and asyncpg (lazy import)
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    asyncpg = None


@dataclass
class Recipe:
    """A successful editing pattern that can be reused."""
    id: str
    user_id: int
    name: str
    description: str
    parameters: Dict[str, Any]
    success_count: int = 0
    created_at: str = ""
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("embedding", None)  # Don't serialize embedding
        return d


@dataclass
class StyleProfile:
    """User's editing style preferences learned over time."""
    user_id: int
    pacing_preference: str = "medium"  # fast, medium, slow
    color_preference: str = "neutral"  # warm, cool, neutral
    audio_preference: str = "balanced"  # speech-focus, music-focus, balanced
    favorite_transitions: List[str] = None
    avoid_patterns: List[str] = None
    
    def __post_init__(self):
        self.favorite_transitions = self.favorite_transitions or []
        self.avoid_patterns = self.avoid_patterns or []


class VectorMemoryStore:
    """
    Long-term memory store using PostgreSQL with pgvector.
    Provides semantic search for user profiles and recipes.
    """
    
    EMBEDDING_DIM = 1536  # OpenAI text-embedding-3-small dimension
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url
        self._pool: Optional[Any] = None
    
    async def _get_pool(self):
        """Lazy initialize connection pool."""
        if not ASYNCPG_AVAILABLE:
            logger.warning("asyncpg_not_available", message="asyncpg package not installed")
            return None
        
        if self._pool is None and self.database_url:
            try:
                self._pool = await asyncpg.create_pool(self.database_url, min_size=2, max_size=10)
                await self._init_schema()
                logger.info("pgvector_connected")
            except Exception as e:
                logger.error("pgvector_connection_failed", error=str(e))
                self._pool = None
        
        return self._pool
    
    async def _init_schema(self):
        """Initialize database schema with pgvector extension."""
        pool = self._pool
        if not pool:
            return
        
        async with pool.acquire() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Recipes table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    parameters JSONB,
                    success_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    embedding vector(1536)
                );
                CREATE INDEX IF NOT EXISTS idx_recipes_user ON recipes(user_id);
            """)
            
            # Style profiles table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS style_profiles (
                    user_id INTEGER PRIMARY KEY,
                    pacing_preference TEXT DEFAULT 'medium',
                    color_preference TEXT DEFAULT 'neutral',
                    audio_preference TEXT DEFAULT 'balanced',
                    favorite_transitions TEXT[] DEFAULT '{}',
                    avoid_patterns TEXT[] DEFAULT '{}',
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            logger.info("pgvector_schema_initialized")
    
    async def save_recipe(self, recipe: Recipe, embedding: Optional[List[float]] = None) -> bool:
        """Save a successful pattern as a reusable recipe."""
        pool = await self._get_pool()
        if not pool:
            return False
        
        try:
            async with pool.acquire() as conn:
                if embedding:
                    await conn.execute("""
                        INSERT INTO recipes (id, user_id, name, description, parameters, success_count, embedding)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (id) DO UPDATE SET
                            success_count = recipes.success_count + 1,
                            parameters = $5
                    """, recipe.id, recipe.user_id, recipe.name, recipe.description,
                        json.dumps(recipe.parameters), recipe.success_count, str(embedding))
                else:
                    await conn.execute("""
                        INSERT INTO recipes (id, user_id, name, description, parameters, success_count)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (id) DO UPDATE SET
                            success_count = recipes.success_count + 1,
                            parameters = $5
                    """, recipe.id, recipe.user_id, recipe.name, recipe.description,
                        json.dumps(recipe.parameters), recipe.success_count)
                
                logger.info("recipe_saved", recipe_id=recipe.id, user_id=recipe.user_id)
                return True
        except Exception as e:
            logger.error("recipe_save_failed", error=str(e))
            return False
    
    async def find_similar_recipes(
        self, 
        user_id: int, 
        query_embedding: List[float],
        limit: int = 5
    ) -> List[Recipe]:
        """Find similar recipes using vector similarity search."""
        pool = await self._get_pool()
        if not pool:
            return []
        
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT id, user_id, name, description, parameters, success_count, created_at
                    FROM recipes
                    WHERE user_id = $1 AND embedding IS NOT NULL
                    ORDER BY embedding <-> $2
                    LIMIT $3
                """, user_id, str(query_embedding), limit)
                
                return [
                    Recipe(
                        id=row["id"],
                        user_id=row["user_id"],
                        name=row["name"],
                        description=row["description"],
                        parameters=json.loads(row["parameters"]) if row["parameters"] else {},
                        success_count=row["success_count"],
                        created_at=str(row["created_at"])
                    )
                    for row in rows
                ]
        except Exception as e:
            logger.error("recipe_search_failed", error=str(e))
            return []
    
    async def get_user_recipes(self, user_id: int, limit: int = 10) -> List[Recipe]:
        """Get user's most successful recipes."""
        pool = await self._get_pool()
        if not pool:
            return []
        
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT id, user_id, name, description, parameters, success_count, created_at
                    FROM recipes
                    WHERE user_id = $1
                    ORDER BY success_count DESC
                    LIMIT $2
                """, user_id, limit)
                
                return [
                    Recipe(
                        id=row["id"],
                        user_id=row["user_id"],
                        name=row["name"],
                        description=row["description"],
                        parameters=json.loads(row["parameters"]) if row["parameters"] else {},
                        success_count=row["success_count"],
                        created_at=str(row["created_at"])
                    )
                    for row in rows
                ]
        except Exception as e:
            logger.error("recipes_get_failed", error=str(e))
            return []
    
    async def get_style_profile(self, user_id: int) -> Optional[StyleProfile]:
        """Get user's style profile."""
        pool = await self._get_pool()
        if not pool:
            return None
        
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM style_profiles WHERE user_id = $1
                """, user_id)
                
                if row:
                    return StyleProfile(
                        user_id=row["user_id"],
                        pacing_preference=row["pacing_preference"],
                        color_preference=row["color_preference"],
                        audio_preference=row["audio_preference"],
                        favorite_transitions=list(row["favorite_transitions"] or []),
                        avoid_patterns=list(row["avoid_patterns"] or [])
                    )
                return None
        except Exception as e:
            logger.error("profile_get_failed", error=str(e))
            return None
    
    async def update_style_profile(self, profile: StyleProfile) -> bool:
        """Update user's style profile."""
        pool = await self._get_pool()
        if not pool:
            return False
        
        try:
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO style_profiles 
                    (user_id, pacing_preference, color_preference, audio_preference, 
                     favorite_transitions, avoid_patterns, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, NOW())
                    ON CONFLICT (user_id) DO UPDATE SET
                        pacing_preference = $2,
                        color_preference = $3,
                        audio_preference = $4,
                        favorite_transitions = $5,
                        avoid_patterns = $6,
                        updated_at = NOW()
                """, profile.user_id, profile.pacing_preference, profile.color_preference,
                    profile.audio_preference, profile.favorite_transitions, profile.avoid_patterns)
                
                logger.info("profile_updated", user_id=profile.user_id)
                return True
        except Exception as e:
            logger.error("profile_update_failed", error=str(e))
            return False
    
    async def close(self):
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None


# Global instance (configured via environment)
vector_store = VectorMemoryStore()
