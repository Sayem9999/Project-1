import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.base import run_agent_prompt
from app.config import settings

async def test_openrouter():
    print("🚀 Testing OpenRouter Integration...")
    
    # Check if key is present
    if not settings.openrouter_api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment.")
        return

    # Use a simple prompt
    system_prompt = "You are a helpful assistant. Return JSON with a 'status' field."
    payload = {"message": "Hello OpenRouter"}
    
    try:
        print(f"📡 Sending request via OpenRouter...")
        # Force openrouter for test if not primary
        result = await run_agent_prompt(
            system_prompt, 
            payload, 
            agent_name="openrouter_test",
            task_type="simple"
        )
        
        print("\n✅ Response Received!")
        print(f"Provider: {result.get('provider')}")
        print(f"Model: {result.get('model')}")
        print(f"Raw Output: {result.get('raw_response')}")
        
    except Exception as e:
        print(f"\n❌ Integration Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
