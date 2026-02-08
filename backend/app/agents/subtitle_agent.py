from .base import run_agent_prompt

PROMPT = """You are the **Subtitle Specialist (AI)** for edit.ai.
Your goal is to generate a **SubRip (.srt)** formatted subtitle file for the video.

**Instructions**:
1.  Listen to the audio accurately.
2.  Format strictly as SRT (Index, Timecode --> Timecode, Text).
3.  Break lines naturally (max 40 chars per line).
4.  Do not add any conversational filler before/after the SRT content.

**Input**:
- Audio/Video Context

**Output**:
- STRICTLY the .srt file content.
"""

async def run(payload: dict) -> dict:
    # Gemini 1.5 Pro is required for long-context audio understanding
    return await run_agent_prompt(PROMPT, payload, model="gemini-1.5-pro")
