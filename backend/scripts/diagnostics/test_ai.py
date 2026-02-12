import asyncio
import os
from app.agents.base import run_agent_prompt

async def test_ai():
    print("=== Testing AI Providers ===")
    
    # Test cases
    tasks = ["simple", "creative", "analytical"]
    
    for task in tasks:
        print(f"\n--- Task Type: {task} ---")
        try:
            result = await run_agent_prompt(
                system_prompt="Return a JSON with a single key 'status' and value 'ok'.",
                payload={"test": True},
                task_type=task,
                agent_name=f"test_{task}"
            )
            print(f"Success! Provider: {result.get('provider')}, Model: {result.get('model')}")
            print(f"Response: {result.get('raw_response')}")
        except Exception as e:
            print(f"FAILED for {task}: {e}")

if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd())
    asyncio.run(test_ai())
