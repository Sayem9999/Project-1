import asyncio
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app.agents.frontend_agent import frontend_agent
from app.agents.backend_agent import backend_agent
from app.agents.analyst_agent import analyst_agent

async def main():
    print("Testing Specialist Agents...")
    
    print("\n--- Frontend Agent ---")
    try:
        res = await frontend_agent.run({"query": "How do I center a div using Tailwind?", "context": "React Component"})
        print(res.get("response", "No response")[:200] + "...")
        print(f"Status: {res.get('status')}")
    except Exception as e:
        print(f"Frontend Error: {e}")

    print("\n--- Backend Agent ---")
    try:
        res = await backend_agent.run({"query": "Create a simple FastAPI endpoint for 'hello world'", "context": "Python 3.11"})
        print(res.get("response", "No response")[:200] + "...")
        print(f"Status: {res.get('status')}")
    except Exception as e:
        print(f"Backend Error: {e}")

    print("\n--- Analyst Agent ---")
    try:
        res = await analyst_agent.run({"query": "Analyze the trade-offs of using Redis vs Memcached", "context": "Caching Strategy"})
        print(res.get("response", "No response")[:200] + "...")
        print(f"Status: {res.get('status')}")
    except Exception as e:
        print(f"Analyst Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
