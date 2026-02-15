import asyncio
import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app.agents.maintenance_agent import maintenance_agent
from app.config import settings

async def main():
    print(f"Testing Autonomy LLM Integration...")
    print(f"Primary Provider: {settings.llm_primary_provider}")
    print(f"OpenAI Key Configured: {bool(settings.openai_api_key)}")
    
    payload = {
        "task": "populate",
        "feature_request": "Create a simple HelloWorld service with a get_message method."
    }
    
    try:
        result = await maintenance_agent.run(payload)
        print("\n=== Result ===")
        print(result)
        
        if result.get("status") == "population_scaffolded":
            print("\n[SUCCESS] LLM generated scaffold successfully.")
        else:
            print("\n[FAILURE] LLM did not return expected status.")
            
    except Exception as e:
        print(f"\n[ERROR] execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
