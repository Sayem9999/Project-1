import httpx
import structlog
from typing import List, Dict, Any
from ..config import settings

logger = structlog.get_logger()

class StockScoutService:
    """
    Service for scouting real stock footage from Pexels and Pixabay.
    """
    
    def __init__(self):
        self.pexels_key = getattr(settings, "pexels_api_key", None)
        self.pixabay_key = getattr(settings, "pixabay_api_key", None)
        
    async def search(self, queries: List[str], limit_per_query: int = 2) -> List[Dict[str, Any]]:
        """Search across multiple providers."""
        results = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            for query in queries:
                # Try Pexels first (high quality)
                if self.pexels_key:
                    pexels_assets = await self._search_pexels(client, query, limit_per_query)
                    results.extend(pexels_assets)
                
                # Try Pixabay if we need more or as fallback
                if self.pixabay_key and len(results) < limit_per_query * len(queries):
                    pixabay_assets = await self._search_pixabay(client, query, limit_per_query)
                    results.extend(pixabay_assets)
                    
        return results

    async def _search_pexels(self, client: httpx.AsyncClient, query: str, limit: int) -> List[Dict[str, Any]]:
        url = f"https://api.pexels.com/videos/search?query={query}&per_page={limit}"
        headers = {"Authorization": self.pexels_key}
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {
                        "url": v["video_files"][0]["link"],
                        "preview_url": v["image"],
                        "provider": "pexels",
                        "tags": [query],
                        "width": v["width"],
                        "height": v["height"],
                        "relevance_score": 0.9
                    }
                    for v in data.get("videos", [])
                ]
        except Exception as e:
            logger.error("pexels_search_failed", query=query, error=str(e))
        return []

    async def _search_pixabay(self, client: httpx.AsyncClient, query: str, limit: int) -> List[Dict[str, Any]]:
        url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={query}&per_page={limit}"
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {
                        "url": v["videos"]["medium"]["url"],
                        "preview_url": v["userImageURL"],
                        "provider": "pixabay",
                        "tags": [query],
                        "width": v["width"],
                        "height": v["height"],
                        "relevance_score": 0.8
                    }
                    for v in data.get("hits", [])
                ]
        except Exception as e:
            logger.error("pixabay_search_failed", query=query, error=str(e))
        return []

stock_scout_service = StockScoutService()
