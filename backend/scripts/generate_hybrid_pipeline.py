import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.workflow_generator_agent import workflow_generator_agent

async def generate_hybrid_pro_pipeline():
    print("🧠 Generating Hybrid Professional Pipeline (Total Compatibility)...")
    
    requirement = """
    Create a professional-grade video editing pipeline for n8n that avoids all high-privilege or version-specific nodes.
    
    Architecture:
    1. Webhook Trigger: Receives job data.
    2. Gemini Director (HTTP Request): Uses standard POST to Google AI.
    3. Status Webhook: Updates ProEdit.
    4. Parallel Agent Logic (HTTP Request): Calls Gemini for Subtitles and Cutting.
    5. ProEdit Render Node (HTTP Request): INSTEAD OF ExecuteCommand, this node calls 'POST http://localhost:8000/api/v1/jobs/render'.
       - This offloads the FFmpeg work to the ProEdit Python worker, which is more reliable.
    6. Final Notification: Backend callback.
    
    This ensures it works on Pinokio even if shell commands or Gemini nodes are blocked.
    """
    
    result = await workflow_generator_agent.run({"description": requirement})
    
    if result["status"] == "success":
        print("EXPORT_BEGIN")
        print(result["workflow_json"])
        print("EXPORT_END")
    else:
        print(f"FAILED: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(generate_hybrid_pro_pipeline())
