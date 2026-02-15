import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.workflow_generator_agent import workflow_generator_agent

async def generate_universal_pro_pipeline():
    print("🧠 Generating Universal Professional Pipeline (HTTP Request nodes)...")
    
    requirement = """
    Create a professional-grade video editing pipeline for n8n.
    IMPORTANT: Use only 'HTTP Request' nodes to call the Gemini API instead of native Gemini nodes to ensure compatibility with older n8n versions.
    
    Workflow Structure:
    1. Webhook trigger (job_id, media_urls).
    2. 'Gemini Director' (HTTP Request calling https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent).
    3. Status Webhook (Update backend).
    4. Parallel Processing:
       - Subtitle Agent (HTTP Gemini)
       - Cutter Agent (HTTP Gemini)
       - Colorist Agent (HTTP Gemini)
    5. 'Gemini QC' (HTTP Gemini) - critique the strategy.
    6. FFmpeg Command node.
    7. Final Callback node.
    
    Ensure all Gemini API calls include the API Key header and proper JSON body structure.
    """
    
    result = await workflow_generator_agent.run({"description": requirement})
    
    if result["status"] == "success":
        print("EXPORT_BEGIN")
        print(result["workflow_json"])
        print("EXPORT_END")
    else:
        print(f"FAILED: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(generate_universal_pro_pipeline())
