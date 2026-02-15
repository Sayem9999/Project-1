import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.workflow_generator_agent import workflow_generator_agent

async def generate_pro_pipeline():
    print("🧠 Generating Professional OpenClaw Gemini Brain Pipeline...")
    
    requirement = """
    Create a professional-grade video editing pipeline for n8n using OpenClaw Gemini Brain logic. 
    1. Webhook trigger receiving job_id and media_urls.
    2. 'Gemini Director' node: Analyzes the creative request and outputs a JSON edit strategy.
    3. Parallel Branches: 
       - Branch A: Subtitle Agent (Word-level timing).
       - Branch B: Cutter Agent (Technical cut points).
       - Branch C: Colorist Agent (LUTs and color correction).
    4. 'Gemini QC' node: Joins branches and critiques the plan, re-routing if quality is low.
    5. FFmpeg Node: Executes the final rendering.
    6. Notification Node: Sends results to the ProEdit callback.
    Include status update webhooks at every major node.
    """
    
    result = await workflow_generator_agent.run({"description": requirement})
    
    if result["status"] == "success":
        print("EXPORT_BEGIN")
        print(result["workflow_json"])
        print("EXPORT_END")
    else:
        print(f"FAILED: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(generate_pro_pipeline())
