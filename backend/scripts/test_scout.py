import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.stock_scout_service import stock_scout_service
from app.agents import scout_agent
from app.config import settings

async def test_scout():
    print("🔍 Testing Stock Scout Intelligence...")
    
    # 1. Test Agent Logic (Formulating Queries)
    test_plan = {
        "directors_vision": "A lonely man walks through a neon-lit city at night, reflecting on his past.",
        "mood": "melancholic",
        "pacing": "slow"
    }
    
    print("\n[AI Agent] Analyzing vision and generating queries...")
    scout_resp = await scout_agent.run({"plan": test_plan})
    print(f" > Search Queries: {scout_resp.search_queries}")
    print(f" > AI Reasoning: {scout_resp.reasoning}")

    # 2. Test Service Logic (Mock/Real API search)
    print("\n[Service] Searching Pexels/Pixabay...")
    # Even without keys, it should handle it gracefully
    assets = await stock_scout_service.search(scout_resp.search_queries[:2])
    
    if assets:
        print(f" ✅ Found {len(assets)} assets!")
        for i, asset in enumerate(assets):
            print(f"   {i+1}. [{asset['provider'].upper()}] {asset['url']}")
    else:
        print(" ⚠️ No assets found (Check API keys in .env: PEXELS_API_KEY, PIXABAY_API_KEY)")

if __name__ == "__main__":
    asyncio.run(test_scout())
