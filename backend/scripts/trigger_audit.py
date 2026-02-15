import asyncio
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app.agents.maintenance_agent import maintenance_agent

async def main():
    print("Triggering maintenance audit...")
    payload = {"task": "audit"}
    try:
        result = await maintenance_agent.run(payload)
        print("\n=== Audit Result ===")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
