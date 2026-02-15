import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.workflow_generator_agent import workflow_generator_agent

async def test_generation():
    print("🚀 Testing Workflow Generator Agent...")
    
    test_query = "Create a workflow that takes a video URL, waits 10 seconds, and then sends a POST request with the status."
    
    result = await workflow_generator_agent.run({"description": test_query})
    
    if result["status"] == "success":
        print("✅ Generation Success!")
        workflow = result["workflow_json"]
        
        # Validate JSON
        try:
            parsed = json.loads(workflow)
            print(f"📊 Nodes generated: {len(parsed.get('nodes', []))}")
            for node in parsed.get('nodes', []):
                print(f"  - [{node.get('type')}] {node.get('name')}")
        except Exception as e:
            print(f"❌ Invalid JSON generated: {e}")
            print("RAW OUTPUT:", workflow)
    else:
        print(f"❌ Generation Failed: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(test_generation())
