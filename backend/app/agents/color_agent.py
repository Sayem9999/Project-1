from .base import run_agent_prompt

PROMPT = """You are the **Expert Colorist Agent**.
You receive instructions from the Lead Director and must generate technical FFmpeg filter parameters.
Your goal: Define the 'eq' or 'colorbalance' filter to match the mood.

**Input**:
- Director Instructions (e.g., "High contrast", "Teal and Orange")
- Theme

**Output**:
Return STRICTLY JSON with:
{
  "ffmpeg_color_filter": "string (e.g., 'eq=contrast=1.2:saturation=1.3', 'colorbalance=rs=.3')",
  "explanation": "Why you chose this filter logic"
}
*Note: Return ONLY the filter string portion.*
"""


async def run(payload: dict) -> dict:
    return await run_agent_prompt(PROMPT, payload, model="gemini-1.5-flash")
