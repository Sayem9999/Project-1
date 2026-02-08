from .base import run_agent_prompt

PROMPT = """You are the **Expert Cutter Agent**.
You receive instructions from the Lead Director and must generate technical FFmpeg filter parameters.
Your goal: Define the 'select' filter to keep the best parts of the video.

**Input**:
- Director Instructions (e.g., "Remove pauses", "Fast cuts")
- Theme

**Output**:
Return STRICTLY JSON with:
{
  "ffmpeg_select_filter": "string (e.g., 'gt(scene,0.3)', 'between(t,0,10)+between(t,15,20)')",
  "explanation": "Why you chose this filter logic"
}
*Note: For this v1, simplify to returning a 'select' expression string compatible with FFmpeg's select filter.*
"""


async def run(payload: dict) -> dict:
    # Upgrade to 1.5 Pro for better video context understanding
    return await run_agent_prompt(PROMPT, payload, model="gemini-1.5-pro")

